library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

matrix_file <- args[1]
out_file    <- args[2]

load(matrix_file, verbose=TRUE)

# https://stackoverflow.com/questions/5888287/running-cor-or-any-variant-over-a-sparse-matrix-in-r
sparse.cor <- function(x) {
    n <- nrow(x)

    cMeans <- colMeans(x)
    cSums <- colSums(x)

    # Calculate the population covariance matrix.
    # There's no need to divide by (n-1) as the std. dev is also calculated the same way.
    # The code is optimized to minize use of memory and expensive operations
    covmat <- tcrossprod(cMeans, (-2*cSums+n*cMeans))
    crossp <- as.matrix(crossprod(x))
    covmat <- covmat+crossp

    sdvec <- sqrt(diag(covmat)) # standard deviations of columns
    covmat/crossprod(t(sdvec)) # correlation matrix
}

print("Calculating correlation matrix")
cor = sparse.cor(X_train)

print("Finding top pairwise correlations")
# http://r.789695.n4.nabble.com/return-only-pairwise-correlations-greater-than-given-value-td4079028.html
cor[upper.tri(cor, TRUE)] <- NA
i <- which(abs(cor) >= 0.7, arr.ind=TRUE)
top <- data.frame(matrix(colnames(cor)[as.vector(i)], ncol=2), value=cor[i])
write.csv(top, file=out_file)

# vim: expandtab sw=4 ts=4
