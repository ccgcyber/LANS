import org.apache.log4j.{Level, Logger}
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.graphx._
import org.apache.spark.sql.SparkSession
import org.apache.spark.rdd.RDD
import org.graphframes.GraphFrame
import org.apache.spark.sql.Row


object Properties {

  def main(args: Array[String]) {

    Logger.getLogger("org").setLevel(Level.OFF)
    Logger.getLogger("akka").setLevel(Level.OFF)
    val conf = new SparkConf().setAppName("Properties")//.setMaster("local[*]")
    val sc = new SparkContext(conf)
    val sqlContext = SparkSession.builder().getOrCreate()
    import sqlContext.implicits._

    val address = sc.broadcast(args(args.length - 1)).value
    for (i <- 0 until args.length - 1) {

    val data = sc.broadcast(args(i)).value
    var edges = sqlContext.read.format("com.databricks.spark.csv").option("header", "true").load(data).select("SrcAddr", "DstAddr")
    edges = edges.withColumnRenamed("SrcAddr", "src").withColumnRenamed("DstAddr", "dst").distinct()
    val n1 = edges.select("src").distinct()
    val n2 = edges.select("dst").distinct()
    val n = n1.union(n2).distinct()
    val nodes = n.withColumnRenamed("src", "id")
    val graph: Graph[Row, Row] = GraphFrame(nodes, edges).toGraphX
    println("-------------------------------------original---------------------------------------")
    println(graph.numVertices)
    println(graph.numEdges)

    val indexTable = graph.vertices.map { case (id, attr) => (id, attr.toString()) }.toDF("id", "IPs")
    val newVertices = graph.vertices.map { case (id, attr) => (id, 1) }
    val newEdges: RDD[Edge[Int]] = graph.edges.map(e => Edge(e.srcId, e.dstId, 1))
    val graph2 = Graph(newVertices, newEdges)

    val InDegree_Distribution = GraphProperties.inDegreeDistribution(graph2).toDF("id", "indegree").cache()
    println("---------------------------degreeDistribution---------------------------------------")
          val OutDegree_Distribution = GraphProperties.outDegreeDistribution(graph2).toDF("id", "outdegree").cache()
          println("---------------------------degreeDistribution---------------------------------------")
          val average_Neighbor_Degree_Distribution = GraphProperties.averageNeighborDegreeDistribution(graph2).toDF("id", "average_neighbor_degree").cache()
          println("----------------------------averageNeighborDegreeDistribution-----------------------")
      //    val page_Rank_Distribution = GraphProperties.pageRankDistribution(graph2).toDF("id", "page_rank").cache()
      //    println("----------------------------pageRankDistribution----------------------------------")
          val triangle_Distribution = GraphProperties.triangleDistribution(graph2).toDF("id", "triangles").cache()
          println("-----------------------------triangleDistribution-----------------------------------")
          val local_Clustering_Coefficient_Distribution = GraphProperties.localClusteringCoefficientDistribution(graph2).toDF("id", "clustering_coefficient").cache()
          println("-----------------------------localClusteringCoefficientDistribution-----------------")
          val kCore_Distribution = KCore.run(graph2, 5).vertices.toDF("id", "kCore").cache()
          println("-----------------------------kCoreDistribution--------------------------------------")

    val results = indexTable.join(InDegree_Distribution, Seq("id"), "left_outer")
              .join(OutDegree_Distribution,Seq("id"), "left_outer")
              .join(average_Neighbor_Degree_Distribution, Seq("id"), "left_outer")
        //      .join(page_Rank_Distribution, Seq("id"), "left_outer")
              .join(triangle_Distribution, Seq("id"), "left_outer")
              .join(local_Clustering_Coefficient_Distribution, Seq("id"), "left_outer")
              .join(kCore_Distribution, Seq("id"), "left_outer")
      .drop(indexTable("id"))
    results.write.format("com.databricks.spark.csv").mode("overwrite").option("header", "true").save(address + "/" + data.substring(0, data.indexOf('.')) + "_properties")
  }

    sc.stop()
  }
}
