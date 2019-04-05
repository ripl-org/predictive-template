library(assertthat)
library(data.table)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

n <- length(args)
outcomes_file   <- args[1]
feature_files   <- args[2:(n-2)]
out_file        <- args[n-1]
train_file      <- args[n]
 
y <- fread(outcomes_file)

train    <- which(y$SUBSET == "TRAINING")
validate <- which(y$SUBSET == "VALIDATION")
test     <- which(y$SUBSET == "TESTING")

y_train    <- y[train,]
y_validate <- y[validate,]
y_test     <- y[test,]

n <- length(feature_files)
X_train    <- vector("list", n)
X_validate <- vector("list", n)
X_test     <- vector("list", n)

for (i in 1:n) {
    print(paste0("Adding ", feature_files[[i]]))
    feature <- fread(feature_files[[i]])
    gc()
    X_train[[i]]    <- Matrix(as.matrix(feature[train,    -c(1)]), sparse=TRUE)
    X_validate[[i]] <- Matrix(as.matrix(feature[validate, -c(1)]), sparse=TRUE)
    X_test[[i]]     <- Matrix(as.matrix(feature[test,     -c(1)]), sparse=TRUE)
}
gc()

X_train    <- do.call("cbind", X_train)
X_validate <- do.call("cbind", X_validate)
X_test     <- do.call("cbind", X_test)

save(X_train, X_validate, X_test,
     y_train, y_validate, y_test,
     file=out_file)

writeMM(X_train, file=train_file)

