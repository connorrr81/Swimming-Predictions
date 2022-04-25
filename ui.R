ui <- fluidPage(
  
  theme = bs_theme(version = 4, bootswatch = "minty"),
  
  # App title ----
  titlePanel("Predictions of the 2020 Olympics Swimming Finals"),
  
  mainPanel(
    fluidRow(
      column(6,
             h4("Actual Results"),
             tableOutput("results")
             ),
      
      column(6,
             h4("Predicted Results"),
             tableOutput("prediction")
             ),
      
      hr(),
      
      column(3,
             selectInput("event_id", 'Please select an event',
                         choices = sort(unique(data$Event))
                         )
      ),
      
      column(3,
             offset=1,
             selectInput("model_id", 'Please select a model',
                         choices = sort(unique(data$Model)))
      )
    )
  )
)
