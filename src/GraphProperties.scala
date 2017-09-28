import org.apache.spark.graphx.{VertexRDD, _}
import scala.collection.mutable.ListBuffer

object GraphProperties {


  def degreeDistribution(graph: Graph[Int, Int]): VertexRDD [Int] = {
    graph.degrees.cache()
  }

  def inDegreeDistribution(graph: Graph[Int, Int]): VertexRDD [Int] = {
    graph.inDegrees.cache()
  }

  def outDegreeDistribution(graph: Graph[Int, Int]): VertexRDD [Int] = {
    graph.outDegrees.cache()
  }

  def averageNeighborDegreeDistribution(graph: Graph[Int, Int]): VertexRDD[Double] = {
    val tempGraph = graph.outerJoinVertices(graph.degrees)((vid, data, attr) => {attr.getOrElse(0)}).cache()
    val VertexRDD = tempGraph.aggregateMessages[(Int, Double)](
      triplet => {
        triplet.sendToDst(1, triplet.srcAttr)
        triplet.sendToSrc(1, triplet.dstAttr)
      },
      (a, b) => (a._1 + b._1, a._2 + b._2)
    ).cache()
    val avgAgeOfNeighborDegree: VertexRDD[Double] = VertexRDD.mapValues((id, value) => value match { case (count, totalAge) => totalAge/count }).cache()
    avgAgeOfNeighborDegree.cache()
  }

  def PageRankDistribution(graph:Graph[Int, Int], initalProbabiltiy: Double = 0.15, numIter: Int = 5): VertexRDD[Double] = {
    // static version of PageRank: the number of iteration set by users
    val pagerankGraph: Graph[Double, Double] = graph.outerJoinVertices(graph.outDegrees){ (vid, vdata, deg) => deg.getOrElse(0)}
      .mapTriplets( e => 1.0 / e.srcAttr ).mapVertices( (id, attr) => 1.0 ).cache()
    def vertexProgram(id: VertexId, attr: Double, msgSum: Double): Double =
      initalProbabiltiy + (1.0 - initalProbabiltiy) * msgSum
    def sendMessage(edge: EdgeTriplet[Double, Double]) =
      Iterator((edge.dstId, edge.srcAttr * edge.attr))
    def messageCombiner(a: Double, b: Double): Double = a + b
    // The initial message received by all vertices in PageRank
    val initialMessage = 0.0
    val resultGraph = Pregel(pagerankGraph, initialMessage, numIter)(vertexProgram, sendMessage, messageCombiner)
    val summ = resultGraph.vertices.values.collect.sum
    resultGraph.mapVertices{case (id, attr) => attr/summ}.vertices.cache()

  }

  def triangleDistribution(graph: Graph[Int, Int]): VertexRDD[Int] ={

    val g = graph.convertToCanonicalEdges().groupEdges((a, b) => a).subgraph(epred = e => e.srcId != e.dstId).cache()
    val neighbors: VertexRDD[ListBuffer[VertexId]]=g.aggregateMessages[ListBuffer[VertexId]](
      triplet => {
        if (triplet.srcId < triplet.dstId) {
          triplet.sendToSrc(ListBuffer(triplet.dstId))
          triplet.sendToDst(ListBuffer(triplet.srcId))
        }
      },
      _++_
    ).cache()
    val setGraph = g.outerJoinVertices(neighbors) {(vid, _, optSet) => optSet.orNull}.cache()
    def edgeCalculate(ctx: EdgeContext[ListBuffer[VertexId], Int, Int]) = {
      assert(ctx.srcAttr != null)
      assert(ctx.dstAttr != null)
      val counter: Int = ctx.srcAttr.intersect(ctx.dstAttr).size
      ctx.sendToSrc(counter)
      ctx.sendToDst(counter)
    }
    val counters:VertexRDD[Int] = setGraph.aggregateMessages(edgeCalculate, _+_)
    val resultGraph = setGraph.outerJoinVertices(counters) {(vid, attr, optSet) => optSet.getOrElse(0)}
    resultGraph.mapVertices{case (id, attr) => attr/2}.vertices.cache()

  }

  def localClusteringCoefficientDistribution(graph:Graph[Int, Int]):VertexRDD[Double] = {

    val g = graph.groupEdges((a, b) => a).cache()
    val nbrSets: VertexRDD[Map[VertexId, Int]] =
    g.collectNeighborIds(EdgeDirection.Either).mapValues { (vid, nbrs) =>
      var nbMap = Map.empty[VertexId, Int]
      var i = 0
      while (i < nbrs.length) {
        val nbId = nbrs(i)
        if(nbId != vid) {
          val count = nbMap.getOrElse(nbId, 0)
          nbMap += (nbId -> (count + 1))
        }
        i += 1
      }
      nbMap
    }.cache()

    val setGraph: Graph[Map[VertexId, Int], Int] = g.outerJoinVertices(nbrSets) {
      (vid, _, optSet) =>  optSet.orNull
    }.cache()

    def edgeFunc(ctx: EdgeContext[Map[VertexId, Int], Int, Double]) {
      assert(ctx.srcAttr != null)
      assert(ctx.dstAttr != null)
      if (ctx.srcId == ctx.dstId) {
        return
      }
      if ((ctx.srcAttr(ctx.dstId) == 2 && ctx.srcId > ctx.dstId) || (ctx.srcId == ctx.dstId)) {
        return
      }

      val (smallId, largeId, smallMap, largeMap) = if (ctx.srcAttr.size < ctx.dstAttr.size) {
        (ctx.srcId, ctx.dstId, ctx.srcAttr, ctx.dstAttr)
      } else {
        (ctx.dstId, ctx.srcId, ctx.dstAttr, ctx.srcAttr)
      }
      val iter = smallMap.iterator
      var smallCount: Int = 0
      var largeCount: Int = 0
      while (iter.hasNext) {
        val valPair = iter.next()
        val vid = valPair._1
        val smallVal = valPair._2
        val largeVal = largeMap.getOrElse(vid, 0)
        if (vid != ctx.srcId && vid != ctx.dstId && largeVal > 0) {
          smallCount += largeVal
          largeCount += smallVal
        }
      }
      if (ctx.srcId == smallId) {
        ctx.sendToSrc(smallCount)
        ctx.sendToDst(largeCount)
      } else {
        ctx.sendToDst(smallCount)
        ctx.sendToSrc(largeCount)
      }
    }

    val counters: VertexRDD[Double] = setGraph.aggregateMessages(edgeFunc, _ + _)

    var nbNumMap = Map[VertexId, Int]()
    nbrSets.collect().foreach { case (vid, nbVal) =>
      nbNumMap += (vid -> nbVal.size)
    }

    g.outerJoinVertices(counters) {
      (vid, _, optCounter: Option[Double]) =>
        val dblCount: Double = optCounter.getOrElse(0)
        val nbNum = nbNumMap(vid)
        assert((dblCount.toInt & 1) == 0)
        if (nbNum > 1) {
          dblCount / (nbNum * (nbNum - 1))
        }
        else {
          0
        }
    }.vertices.cache()
  }
//
//    def harmonicCentralityDistribution(graph: Graph[Int, Int]): VertexRDD[Double] ={
//
//          type NMap = immutable.Map[Int, HLL]
//          val BIT_SIZE = 16
//          val hll = new HyperLogLogMonoid(BIT_SIZE)
//
//          def addMaps(nmap1: NMap, nmap2: NMap): NMap = {
//            (nmap1.keySet ++ nmap2.keySet).map({
//              k => k -> (
//                nmap1.getOrElse(k, new HyperLogLogMonoid(BIT_SIZE).zero) +
//                  nmap2.getOrElse(k, new HyperLogLogMonoid(BIT_SIZE).zero))
//            }).toMap
//          }
//
//          def isEqual(a: NMap, b: NMap): Boolean = {
//            val newVal = addMaps(a, b)
//            for (key <- b.keySet) {
//              val oldSize = a.getOrElse(key, new HyperLogLogMonoid(BIT_SIZE).zero).estimatedSize
//              val newSize = newVal.getOrElse(key, new HyperLogLogMonoid(BIT_SIZE).zero).estimatedSize
//              if (oldSize != newSize) {
//                return false
//              }
//            }
//            true
//          }
//
//          def calculateForNode(id:VertexId, distances: NMap): Double = {
//            var harmonic = 0.0
//            val sorted = distances.filterKeys(_ > 0).toSeq.sortBy(_._1)
//            var total = hll.create(id.toString.getBytes)
//            for ((step, v) <- sorted) {
//              val before = total.estimatedSize
//              total += v
//              val after = total.estimatedSize
//              harmonic += BigDecimal((after - before) / step)
//                .setScale(5, BigDecimal.RoundingMode.HALF_UP)
//                .toDouble
//            }
//            harmonic
//          }
//
//          def harmonicCentrality(graph: Graph[Int, Int], maxDistance: Int = 6): Graph[Double, Int] = {
//
//            val initGraph: Graph[NMap, Int] = graph.mapVertices(
//              (id: VertexId, v: Int) => immutable.Map[Int, HLL](
//                (0, hll.create(id.toString.getBytes))
//              )
//            )
//
//            val initMessage = immutable.Map[Int, HLL](0 -> new HyperLogLogMonoid(BIT_SIZE).zero)
//
//            def incrementNMap(p: NMap): NMap = p.filterKeys(_ < maxDistance).map {
//              case (v, d) => (v + 1) -> d
//            }
//
//            def vertexProgram(x: VertexId, vertexValue: NMap, message: NMap) = {
//              addMaps(vertexValue, message)
//            }
//
//            def sendMessage(edge: EdgeTriplet[NMap, Int]): Iterator[(VertexId, NMap)] = {
//              val newAttrSrc = incrementNMap(edge.srcAttr)
//              val newAttrDst = incrementNMap(edge.dstAttr)
//
//              if (!isEqual(edge.dstAttr, newAttrSrc)) {
//                Iterator((edge.dstId, newAttrSrc))
//              }else if(!isEqual(edge.srcAttr, newAttrDst)){
//                Iterator((edge.srcId, newAttrDst))
//              } else {
//                Iterator.empty
//              }
//            }
//            def messageCombiner(a: NMap, b: NMap): NMap = {
//              addMaps(a, b)
//            }
//            val distances = Pregel(initGraph, initMessage, activeDirection = EdgeDirection.Either)(
//              vertexProgram, sendMessage, messageCombiner)
//            distances.mapVertices[Double]((id: VertexId, vertexValue: NMap) => calculateForNode(id, vertexValue))
//          }
//          val temp = harmonicCentrality(graph)
//          temp.vertices
//    }
//


}
