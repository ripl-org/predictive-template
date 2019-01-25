library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file   <- args[2]
outcome_name  <- args[3]
beta_file     <- args[4]
out_file      <- args[5]

load(matrix_file, verbose=TRUE)
y_train <- y_train[,c(outcome_name)]

beta <- read.csv(beta_file)
names(beta) <- c("var", "coef")
selected <- beta[which(beta$coef != 0), "var"]
print(selected)

X_train <- X_train[,selected]

model <- glm.fit(x=X_train, y=y_train, family=binomial())

write.csv(summary.glm(model), file=out_file)
