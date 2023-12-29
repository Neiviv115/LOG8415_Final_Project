#!/bin/bash


export HADOOP_HOME="/usr/local/hadoop"
export JAVA_HOME="/usr/lib/jvm/jre-openjdk"
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin

mkdir datasets

curl -L -o datasets/f1.txt https://tinyurl.com/4vxdw3pa
curl -L -o datasets/f2.txt https://tinyurl.com/kh9excea
curl -L -o datasets/f3.txt https://tinyurl.com/dybs9bnk
curl -L -o datasets/f4.txt https://tinyurl.com/datumz6m
curl -L -o datasets/f5.txt https://tinyurl.com/j4j4xdw6
curl -L -o datasets/f6.txt https://tinyurl.com/ym8s5fm4
curl -L -o datasets/f7.txt https://tinyurl.com/2h6a75nk
curl -L -o datasets/f8.txt https://tinyurl.com/vwvram8
curl -L -o datasets/f9.txt https://tinyurl.com/weh83uyn

files=("f1.txt" "f2.txt" "f3.txt" "f4.txt" "f5.txt" "f6.txt" "f7.txt" "f8.txt" "f9.txt")


start-dfs.sh



hdfs dfs -mkdir -p "/user/$(whoami)"
hdfs dfs -rm -r datasets
hdfs dfs -mkdir datasets
hdfs dfs -copyFromLocal datasets/* datasets/


echo "method,file,time" > comparison_spark.csv
echo "Running Hadoop WordCount for 9 files, 3 times each" > trace_spark_hadoop.txt

global_start_time=$(date +%s.%3N)
for file in "${files[@]}"; do
    input_file="datasets/$file"
    echo "For file $input_file:" >> trace_spark_hadoop.txt
    for ((i=1; i<=3; i++)); do
        output_dir="output_${file}"
        hdfs dfs -rm -r $output_dir
        # Run Hadoop wordcount and record time
        start_time=$(date +%s.%3N)
        hadoop jar "/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar" wordcount $input_file $output_dir
        end_time=$(date +%s.%3N)
        elapsed_time=$(echo "$end_time - $start_time" | bc)
         # Append time to comparison.csv
        echo "hadoop,$file,$elapsed_time" >> comparison_spark.csv
        echo "run $i in $elapsed_time seconds" >> trace_spark_hadoop.txt
    done
done

global_end_time=$(date +%s.%3N)
elapsed_time=$(echo "$global_end_time - $global_start_time" | bc)
echo "Time taken by 3x9 hadoop wordcounts: ${elapsed_time} milliseconds" >> trace_spark_hadoop.txt

stop-dfs.sh

echo "
#######

Running Spark WordCount for 9 files, 3 times each" >> trace_spark_hadoop.txt

rm -rf spark_output
mkdir spark_output

global_start_time=$(date +%s.%3N)
for file in "${files[@]}"; do
    input_file="datasets/$file"
    echo "For file $input_file:" >> trace_spark_hadoop.txt
    for ((i=1; i<=3; i++)); do
        output_dir="spark_output/out_${file%.txt}"
        rm -rf $output_dir
        # Run Spark wordcount and record time
        start_time=$(date +%s.%3N)
        python3 spark_wordcount.py $input_file $output_dir
        end_time=$(date +%s.%3N)
        elapsed_time=$(echo "$end_time - $start_time" | bc)
         # Append time to comparison.csv
        echo "spark,$file,$elapsed_time" >> comparison_spark.csv
        echo "run $i in $elapsed_time seconds" >> trace_spark_hadoop.txt
    done
done

global_end_time=$(date +%s.%3N)
elapsed_time=$(echo "$global_end_time - $global_start_time" | bc)
echo "Time taken by 3x9 spark wordcounts: ${elapsed_time} seconds" >> trace_spark_hadoop.txt

