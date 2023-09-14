# Install and load required packages
library(dplyr)
library(yaml)


# Read the YAML file
yaml_data <- yaml.load_file("diff/pubmed-sc-genomics-7days.yaml")
n <- length(yaml_data)

## load IF journal table and convert all capital letters to small
if_table <- read.table("diff/jcr_journal_impact_factors_2019.txt", header = TRUE, sep = "\t")
head(if_table)
if_table$name_small <- tolower(if_table$Full.Journal.Title)


journal_values <- character()
rank_values <- integer()
# Iterate through each paper, lower letters and add rank category
for (i in 1:n) {
    yaml_data[[i]]$journal <- tolower(yaml_data[[i]]$journal)
    journal_values <- c(journal_values, yaml_data[[i]]$journal)
    yaml_data[[i]]$if_rank <- if_table$Rank[if_table$name_small %in% yaml_data[[i]]$journal]
    rank_values <- c(rank_values, yaml_data[[i]]$if_rank)
    
}

# save the updated yml file
yaml_string <- as.yaml(yaml_data)
writeLines(yaml_string, "diff/pubmed-sc-genomics-7days_rank.yaml")


