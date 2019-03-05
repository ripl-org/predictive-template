library(assertthat)
library(AUC)
library(Matrix)

args <- commandArgs(trailingOnly=TRUE)

set.seed(args[1])

matrix_file  <- args[2]
outcome_name <- args[3]
beta_file    <- args[4]
out_file     <- args[5]
pred_file    <- args[6]

load(matrix_file, verbose=TRUE)
y_train <- y_train[,c(outcome_name)]

beta <- read.csv(beta_file, stringsAsFactors=FALSE)
selected <- beta[which(beta$freq > 90), "var"]
print(selected)

X_train <- X_train[,selected]

k <- kappa(X_train, exact=TRUE)
print(paste0("condition number (kappa): ", k))
assert_that(k < 100)

model <- glm.fit(x=X_train, y=y_train, family=binomial())
params <- summary.glm(model)$coefficients

# Convert coefficients to odds ratios and standard errors to 95% C.I.
odds <- exp(params[,1])
ci_lower <- exp(params[,1] - 1.96*params[,2])
ci_upper <- exp(params[,1] + 1.96*params[,2])
write.csv(data.frame(var=selected, odds=odds, ci_lower=ci_lower, ci_upper=ci_upper, p=params[,4]),
          file=out_file, row.names=FALSE)

# Predict on test data with OLS
X_test <- cbind(1, X_test[,selected])
coef <- rbind(1, as.matrix(model$coef))
eta <- as.matrix(X_test) %*% as.matrix(coef)
riipl_id <- y_test[,c("RIIPL_ID")]
y_pred <- exp(eta)/(1 + exp(eta))
y_test <- y_test[,c(outcome_name)]
print(paste0("auc: ", auc(roc(y_pred, as.factor(y_test)))))
write.csv(data.frame(RIIPL_ID=riipl_id, y_pred=y_pred, y_test=y_test), file=pred_file, row.names=FALSE)

