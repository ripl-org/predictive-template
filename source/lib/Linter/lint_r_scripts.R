REPO_ROOT <- Sys.getenv("REPO_ROOT")

library(lintr)

args <- commandArgs(trailingOnly = TRUE)
script_root <- args[1]
log_root <- args[2]

main <- function() {
    lint_dir(script_root, log_root)
}

lint_dir <- function(script_root, log_root) {
    files <- as.list(paste0(script_root, "/",
                    list.files(path = script_root, recursive = TRUE, pattern = "\\.R$")))
    linted <- sapply(sapply(files, lint,
                            linters = with_defaults(line_length_linter = line_length_linter(100)),
                            simplify = FALSE),
                    function(linted_file) {
                        linted_file <- as.data.frame(linted_file)
                        return(paste0(linted_file$filename, ":",
                                      linted_file$line_number, ":",
                                      linted_file$column_number, ": ",
                                      linted_file$type, ": ",
                                      linted_file$message,
                                      "\n"))
                    }, simplify = FALSE)
    lint_files <- paste0(log_root, "/", files, "lint")

    invisible(sapply(unique(dirname(lint_files)),
                     dir.create, recursive = TRUE, showWarnings = FALSE))
    invisible(file.create(lint_files))
    mapply(write, linted, file = lint_files)
    write(unlist(linted), file = paste0(log_root, "/all_linted.Rlint"))
}

main()
