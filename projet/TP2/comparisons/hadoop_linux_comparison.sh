#!/bin/bash

export HADOOP_HOME="/usr/local/hadoop"
export JAVA_HOME="/usr/lib/jvm/jre-openjdk"
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin


wget http://www.gutenberg.org/cache/epub/4300/pg4300.txt

echo "method,time" > comparison_linux.csv
echo "Starting wordcounts using Linux commands " > compare_linux.txt

mkdir linux_output

global_start_time=$(date +%s%3N)
for i in {1..10}; do
    start_time=$(date +%s%3N)
    cat pg4300.txt | tr -s ' ' '\n' | sort | uniq -c > linux_output/output.txt
    end_time=$(date +%s%3N)
    elapsed_time=$((end_time - start_time))
    echo "Time taken by 1 linux wordcount: ${elapsed_time} milliseconds">> compare_linux.txt
    echo "linux,$elapsed_time" >> comparison_linux.csv
done

global_end_time=$(date +%s%3N)
elapsed_time=$((global_end_time - global_start_time))
echo "Time taken by 10 linux wordcounts: ${elapsed_time} milliseconds">> compare_linux.txt


echo "
#########
" >> compare_linux.txt

start-dfs.sh


echo "Starting wordcounts using Hadoop" >> compare_linux.txt

hdfs dfs -mkdir -p "/user/$(whoami)"
hdfs dfs -mkdir input

dfs dfs -rm input
hdfs dfs -put pg4300.txt input

global_start_time=$(date +%s%3N)
for i in {1..10}; do
    hdfs dfs -rm output
    start_time=$(date +%s%3N)
    hadoop jar "/usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar" wordcount input output
    end_time=$(date +%s%3N)
    elapsed_time=$((end_time - start_time))
    echo "Time taken by 1 hadoop wordcount: ${elapsed_time} milliseconds" >> compare_linux.txt
    echo "hadoop,$elapsed_time" >> comparison_linux.csv
done

global_end_time=$(date +%s%3N)
elapsed_time=$((global_end_time - global_start_time))
echo "Time taken by 10 hadoop wordcount: ${elapsed_time} milliseconds" >> compare_linux.txt

stop-dfs.sh

