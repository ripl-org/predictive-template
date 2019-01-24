library(gamlr)
library(PRROC)

gammas <- c(0,1,10,100,1000)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file   <- args[2]
outcome_name  <- args[3]
model_file    <- args[4]
beta_file     <- args[5]

load(matrix_file, verbose=TRUE)

y_train    <- y_train[,c(outcome_name)]
y_validate <- y_validate[,c(outcome_name)]
y_test     <- y_test[,c(outcome_name)]

# Grid search for model with best gamma and lambda
models <- lapply(gammas, function(gamma) {
  model <- gamlr(x=X_train, y=y_train, family="binomial", gamma=gamma, standardize=FALSE)
  model$auprcs <- sapply(1:100, function(i) {
    y_predicted <- predict(model, newdata=X_validate, type="response", select=i)
    return(pr.curve(y_predicted, weights.class0=y_validate)$auc.integral)
  })
  model$auprc <- max(model$auprcs)
  model$best_lambda <- which.max(model$auprcs)
  return(model)
})

best_model <- which.max(lapply(models, function(model) { model$auprc }))
model <- models[[best_model]]

best_gamma  <- gammas[best_model]
print(paste0("best gamma: ", best_gamma))

best_lambda <- model$best_lambda
print(paste0("best lambda: ", best_lambda))

y_predicted <- predict(model, newdata=X_test, type="response", select=model$best_lambda)

save(model, best_gamma, y_predicted, y_test, file=model_file)
write.csv(model$beta[,best_lambda], file=beta_file)
