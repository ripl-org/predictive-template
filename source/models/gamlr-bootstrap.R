library(AUC)
library(gamlr)
library(Matrix)

gammas <- c(0,1,10)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file   <- args[2]
outcome_name  <- args[3]
bootstrap     <- strtoi(args[4])
model_file    <- args[5]
beta_file     <- args[6]

load(matrix_file, verbose=TRUE)

# Generate a bootstrap sample
set.seed(sample(2147483647, bootstrap+1)[bootstrap+1])
n <- nrow(X_train)
idx <- sample(1:n, n, replace=TRUE)
X_train <- X_train[idx,]
y_train    <- y_train[idx,c(outcome_name)]

y_validate <- as.factor(y_validate[,c(outcome_name)])
y_test     <- y_test[,c(outcome_name)]

# Grid search for model with best gamma and lambda
models <- lapply(gammas, function(gamma) {
  model <- gamlr(x=X_train, y=y_train, family="binomial", gamma=gamma, standardize=FALSE)
  model$aucs <- sapply(1:100, function(i) {
    y_predicted <- predict(model, newdata=X_validate, type="response", select=i)
    return(auc(roc(y_predicted, y_validate)))
  })
  model$auc <- max(model$aucs)
  model$best_lambda <- which.max(model$aucs)
  return(model)
})

best_auc <- max(sapply(models, function(model) { model$auc }))
print(paste0("best auc: ", best_auc))

best_model <- which.max(lapply(models, function(model) { model$auc }))
model <- models[[best_model]]

best_gamma  <- gammas[best_model]
print(paste0("best gamma: ", best_gamma))

best_lambda <- model$best_lambda
print(paste0("best lambda: ", best_lambda))

y_predicted <- predict(model, newdata=X_test, type="response", select=model$best_lambda)

save(model, best_auc, best_gamma, best_lambda, y_predicted, y_test, file=model_file)
write.csv(model$beta[,best_lambda], file=beta_file)
