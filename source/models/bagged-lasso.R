library(AUC)
library(gamlr)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

model_file  <- args[1]
model_files <- args[2:length(args)-1]
out_file    <- args[length(args)]

load(model_file)
y_pred_avg <- y_predicted

for (model_file in model_files) {
    load(model_file)
    y_pred_avg <- y_pred_avg + y_predicted
}

y_pred_avg <- y_pred_avg / (length(model_files) + 1)
colnames(y_pred_avg) <- "y_pred"

print(paste0("auc: ", auc(roc(y_pred_avg, as.factor(y_test)))))
write.csv(data.frame(y_pred=y_pred_avg, y_test=y_test), file=out_file, row.names=FALSE)
