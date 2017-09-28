#!/usr/bin/env Rscript

unlink("temp", recursive=TRUE)
dir.create("temp",showWarnings = FALSE)
s <- scan("Configuration.txt", what="character", sep=NULL)
for (i in 2: (length(s)-1)){
    
    start <- which(strsplit(s[i], "")[[1]]=="/")+1
    end <- which(strsplit(s[i], "")[[1]]==".")-1
    dataDir <- paste(substr(s[i], start, end), "_properties", sep="")
    print(dataDir)
    files <- list.files(dataDir)
    data <- NULL
    for (k in 1:length(files)) {
        if(substr(files[k], 1, 4) == "part"){
            temp <- tryCatch(read.csv(paste(dataDir, '/', files[k], sep = ""), header = TRUE), error=function(e) NULL)
            data <- rbind(data, temp)
        }
    }
    data[is.na(data)] <- 0
    data$IPs <- gsub("\\[|\\]", "",as.character(data$IPs))
    write.csv(data, file = paste("temp/","Properties", substr(s[i], start, end), ".csv", sep=""), row.names = FALSE)
    unlink(dataDir , recursive=TRUE)
}
unlink("spark-warehouse" , recursive=TRUE)
quit()
