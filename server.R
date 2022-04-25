server <- function(input, output) {
  
  output$results <- renderTable({
    data %>% 
      filter(Event == input$event_id) %>%
      select(c("Name", "Time")) %>%
      arrange(Time) %>%
      distinct()
  })
  
  output$prediction <- renderTable({
    selected_model <- input$model_id
    data %>% 
      filter(Event == input$event_id,
             Model == selected_model) %>%
      select(c("Name", "Time_Predicted")) %>%
      arrange(Time_Predicted)
  })
}