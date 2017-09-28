import org.apache.spark.graphx._
import scala.math._
import scala.reflect.ClassTag

object KCore {

  def run[VD: ClassTag, ED: ClassTag](graph: Graph[VD, ED], kmax: Int, kmin: Int = 1): Graph[Int, ED] = {

    var g = graph.outerJoinVertices(graph.degrees)((vid, oldData, newData) => (newData.getOrElse(0), true)).cache
    val degrees = graph.degrees
    val numVertices = degrees.count
    var curK = kmin
    while (curK <= kmax) {
      g = computeCurrentKCore(g, curK).cache
      val testK = curK
      val vCount = g.vertices.filter{ case (vid, (vd, _)) => vd >= testK}.count()
      val eCount = g.triplets.map{t => t.srcAttr._1 >= testK && t.dstAttr._1 >= testK }.count()
      curK += 1
    }
    g.mapVertices({ case (_, (k, _)) => k})
  }

  def computeCurrentKCore[ED: ClassTag](graph: Graph[(Int, Boolean), ED], k: Int) = {
    def sendMsg(et: EdgeTriplet[(Int, Boolean), ED]): Iterator[(VertexId, (Int, Boolean))] = {
      if (!et.srcAttr._2 || !et.dstAttr._2) {
        // if either vertex has already been turned off we do nothing
        Iterator.empty
      } else if (et.srcAttr._1 < k && et.dstAttr._1 < k) {
        // tell both vertices to turn off but don't need change count value
        Iterator((et.srcId, (0, false)), (et.dstId, (0, false)))
      } else if (et.srcAttr._1 < k) {
        // if src is being pruned, tell dst to subtract from vertex count but don't turn off
        Iterator((et.srcId, (0, false)), (et.dstId, (1, true)))
      } else if (et.dstAttr._1 < k) {
        // if dst is being pruned, tell src to subtract from vertex count but don't turn off
        Iterator((et.dstId, (0, false)), (et.srcId, (1, true)))
      } else {
        // no-op but keep these vertices active?
        // Iterator((et.srcId, (0, true)), (et.dstId, (0, true)))
        Iterator.empty
      }
    }

    // subtracts removed neighbors from neighbor count and tells vertex whether it was turned off or not
    def mergeMsg(m1: (Int, Boolean), m2: (Int, Boolean)): (Int, Boolean) = {
      (m1._1 + m2._1, m1._2 && m2._2)
    }

    def vProg(vid: VertexId, data: (Int, Boolean), update: (Int, Boolean)): (Int, Boolean) = {
      var newCount = data._1
      var on = data._2
      if (on) {
        newCount = max(k - 1, data._1 - update._1)
        on = update._2
      }
      (newCount, on)
    }
    // Note that initial message should have no effect
    Pregel(graph, (0, true))(vProg, sendMsg, mergeMsg).cache()
  }
}