source("test_func.R")

parity <- function(number) {
    list(parity = if (as.integer(number) %% 2 == 0) "even" else "odd")
}

#' A nullary function that returns the current version of R
#'
#' @return character
#' @export
#'
#' @examples
#' hello()
hello <- function() {
    list(response = paste("Hello from", version$version.string, FCNdirectory, sep=","))
}