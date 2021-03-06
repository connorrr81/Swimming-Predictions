# Swimming-Predictions
To what extent can competitive swimming results be predicted? I aim to use various machine learning techniques to predict the 2020 Olympic swimming results given data on historical swims. 

What is the point in all this? Swimming is regarded, by swim fans, as a relatively forseeable sport. There are athletes that we know will take Gold at the next World Championships or Olympics, for example Caeleb Dressel winning the 100 Free and Adam Peaty storming the 100 Breaststroke. At the elite level, the variance of swimmer's all-out times are in the realm of milliseconds. Though when it comes to the races with more of a level playing field, the forecasts from swim analysts are generally reduced to hunches. The magazine SwimSwam lead the number crunching game, and their knowledge of the state of every swimmer's training, which drives their analysis, is impressive. However, I have not seen an online tool that performs data-driven predictions. There are a behemouth of factors that determine the athlete fitness and competition readiness, so I expect this project will be feature-engineering heavy.

I'm doing this for a bit of fun. Growing up as a competitive swimmer, I spent hours and hours trawling through swimming data, so I knew the data for swimming results are out there. Now I'm building on my data science toolkit, I just had to give it a go. 

## Data Source
The data was obtained from swimrankings (https://www.swimrankings.net/index.php?page=home) which holds a database containing (most) results from elite-level competitions all over the world. Their data is based on information from the European Swimming Federation (LEN) rankings database and the results and ranking database of national swimming federations. 

## Methodology
### Web scraping
Swimrankings have a webpage containing a list of the top 100 male and female athletes, selected by their best alltime result according to the FINA points table. This list would contain the majority of the swimmers who made an Olympic final in Tokyo. On the webpage one can click onto the athlete's profile and see their current personal bests and personal stats (i.e. DOB and Nation), I used BeautifulSoup to find these links and navigate through the website. To limit the amount of unneccessary data in our analysis, I found the events where that particular athlete's PB has greater than 900 FINA points (1000 = WR), these are likely the event that swimmer swims at the games. Clicking on the event name on this page takes you to a table of historical swims for that swimmer and event, Bingo. The web scraper pulls together these tables for the top 100 swimmers (as of 2021). Now on to the fun bit....  

### Feature Engineering
So far we've managed to extract the time (mm:ss), date, location and event for all the recorded swims, up to and including the Olympics, for our top 100 swimmers. Along with the swimmer's nation, club and DOB. To keep our regressors happy with a numerical dependent variable, the swim time was converted to seconds. The following features were created with the hope of increasing model efficacy:
- age_at_swim: the age of the swimmer, days, at the time of swim.
- month: from date feature
- year: from date feature
- PB_at_swim: the swimmer's personal best at the time of swim.
- competition_flag: character indicating the type of competition the historical swim was swam at, O = Olympics, W = World Championships, N = Other.
- finals_flag: character indicating whether or not the swim was a heat or final swim, as swimmers tend to save themselves in heats. Identified by looking at swims in the same event, location and week.
- time_change_since_covid: difference between average time before the pandemic (2019-20) and after (2020-).


### Models
#### Multiple Linear Regression
First tried out a linear model with time as the dependent variable and all predicotrs mentioned above (to start with). There were around 8000 observations with 12 predictors so did not bother with regularisation techniques such as LASSO or Ridge regression. After fitting the full model, I undertook a manual process of eliminating variables using t-tests on the predicted coefficients and implemented a Likelihood ratio test to determine if the reduced model performs as well as the larger. Once satisfied with my model I ensure the assumptions for linear regression are met:
- There is a linear relationship between the independent variables and the dependent variable.
- The error terms of the model are normally distributed.
- The predictors used in the regression are not correlated with each other.
- No Autocorrelations in the residuals
- Error terms are homoscedastic

#### Random Forest

#### XGBoost



## Visualisation
Aiming to build an Rshiny app showing the predicted swims against true swims for each model, alongside the test rmspe.
