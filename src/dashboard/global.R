library(shiny)
library(dplyr)
library(bslib)
library(rsconnect)

data <- read.csv("predicted_times.csv")

data <- data %>% rename(Time = Time..s.,
                        Time_Predicted = value)
