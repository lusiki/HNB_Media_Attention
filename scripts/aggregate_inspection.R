# Read existing scored records; emit publication-safe aggregates only. No model fitting.
suppressPackageStartupMessages(library(data.table))
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
site <- normalizePath(args[1],winslash='/')
scored <- normalizePath(args[2],winslash='/')
a <- as.data.table(readRDS(scored))
a[, DATE:=as.Date(DATE)]
src23 <- unique(a[DATE>=as.Date('2023-01-01') & DATE<as.Date('2024-01-01')]$FROM)
src24 <- unique(a[DATE>=as.Date('2024-07-01') & DATE<as.Date('2025-01-01')]$FROM)
common <- intersect(src23,src24)
periods <- fread(file.path(site,'public/data/monthly-series.csv'))$period
a[,period:=format(DATE,'%Y-%m')]
a <- a[period%in%periods]
stopifnot(all(is.finite(a$REACH)),all(is.finite(a$w_i)),!anyNA(a$infl_relevant))
a[,weight:=w_i*REACH*infl_relevant]
summary_list <- list(); domain_list <- list()
for(sample in c('primary','common')) {
  z <- if(sample=='common') a[FROM%in%common] else a
  src <- z[,.(items=.N,relevant_items=sum(infl_relevant),weight=sum(weight)),by=.(period,source=FROM)]
  ss <- src[,.(source_labels=.N,weighted_sources=sum(weight>0),top5_source_share=sum(head(sort(weight,decreasing=TRUE),5))/sum(weight),weight_hhi=sum((weight/sum(weight))^2)),by=period]
  item <- z[,.(items=.N,relevant_items=sum(infl_relevant),numerator=sum(weight),top10_item_share=sum(head(sort(weight,decreasing=TRUE),10))/sum(weight)),by=period]
  summary_list[[sample]] <- merge(ss,item,by='period')[,sample:=sample]
  # Publish only domain-form labels. Social account identifiers never leave this process.
  domains <- src[grepl('^[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}$',source) & relevant_items>0]
  domains[,sample:=sample]
  domain_list[[sample]] <- domains
}
out <- file.path(site,'private/inspection-aggregates');dir.create(out,recursive=TRUE,showWarnings=FALSE)
fwrite(rbindlist(summary_list),file.path(out,'concentration.csv'))
fwrite(rbindlist(domain_list),file.path(out,'domains.csv'))
fwrite(a[,.(items=.N),by=.(channel=SOURCE_TYPE)][order(channel)],file.path(out,'channels.csv'))
cat('Aggregated',nrow(a),'scored records;',length(common),'common source labels. No article records exported.\n')
