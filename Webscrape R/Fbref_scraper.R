# remember, we need to ensure we've installed the packages we need, but we need to do this very infrequently ( to run the 'install' lines below, simply delete the '#' before the code:
# install.packages("devtools")
# install.packages("xlsx")
# install.packages("tidyverse")
# install.packages("ggrepel")
# devtools::install_github("JaseZiv/worldfootballR", ref = "main")

# once it's been installed, then we need to load the functions (code to let you get the data you want) in the library (this needs to be done every time you want to run your script)
library(worldfootballR)
library(tidyverse)
library(xlsx)
library(dplyr)
library(tidyr)



# now let's get our season team shooting data from FBref:
prem_2021_shooting <- get_season_team_stats(country = "ENG", gender = "M", season_end_year = "2021", tier = "1st", stat_type = "shooting")
view(prem_2021_shooting)

# to save the file as a csv:
write.csv(x= prem_2021_shooting, file = "EPL_shooting_2021_season.csv", row.names = FALSE)
# or we can save an .xlsx file:
write.xlsx(x= prem_2021_shooting, file = "EPL_shooting_2021_season.xlsx", row.names = FALSE)

########################################################################################


# get our data ready for plotting
prem_2021_shooting %>% 
  # filter out only the team shooting data, not their opponents also
  filter(Team_or_Opponent == "team") %>% 
  # create a new column that removes penalties from the team's goal total
  mutate(non_P_Gls = Gls_Standard - PK_Standard) %>% 
  # start plotting:
  ggplot(aes(x= npxG_Expected, y= non_P_Gls)) +
  # add a line through the plot with slope =  1 and the yintercept = 0
  geom_abline(slope = 1, intercept = 0, colour = "red", linetype=2) +
  # we want to make it a scatter plot
  geom_point(size=6, colour="midnightblue", fill="midnightblue", alpha = 0.4, shape=21) +
  # lets also add team name labels
  ggrepel::geom_text_repel(aes(label = Squad), colour = "midnightblue", size=5) + 
  # limit the x and y-axis to start at 10 and finish at 100
  scale_x_continuous(limits = c(10,100), name = "Non-Pen xG") +
  scale_y_continuous(limits = c(10,100), "Non-Pen Goals") +
  ggtitle("DID TEAMS SCORE AS EXPECTED?") +
  # apply a pre-programmed general theme:
  theme_minimal() +
  # but then we can customise our plot even more - first we make the background black:
  # change the title and subtitle format
  theme(plot.title = element_text(size=20, face="bold"), plot.subtitle = element_text(size=22, colour="grey30"),
        # and change where the plot is aligned - in this case it's left-aligned
        plot.title.position = "plot", plot.caption.position = "plot",
        # change the size of aixs titles and text
        axis.title = element_text(size=16), axis.text = element_text(size = 14))


################################################################################

# first we will create a new data set of only the team's performance, and not how their opponents played against them
prem_team <- prem_2021_shooting %>% 
  filter(Team_or_Opponent == "team")

# now we calculate the Pearson correlation
cor(prem_team$Gls_Standard, prem_team$xG_Expected)


################################################################################


