# remember, we need to ensure we've installed the packages we need, but we need to do this very infrequently ( to run the 'install' lines below, simply delete the '#' before the code:
# install.packages("devtools")
# install.packages("xlsx")
# install.packages("tidyverse")
# install.packages("ggrepel")
# devtools::install_github("JaseZiv/worldfootballR", ref = "main")
library(worldfootballR)

team_urls <- understat_team_meta(team_name = c("Liverpool", "Manchester City"))
#team_urls

# to get the EPL results:
# league - xG e results
epl_results <- understat_league_match_results(league = "EPL", season_start_year = 2020)
dplyr::glimpse(epl_results)

view(epl_results)

#################################################

# shot location

#league
ligue1_shot_location <- understat_league_season_shots(league = "Ligue 1", season_start_year = 2022)
view(ligue1_shot_location)

# shots de um jogo
wba_liv_shots <- understat_match_shots(match_url = "https://understat.com/match/14789")
dplyr::glimpse(wba_liv_shots)
view(wba_liv_shots)


# for one team:
man_city_shots <- understat_team_season_shots(team_url = "https://understat.com/team/Manchester_City/2020")
dplyr::glimpse(man_city_shots)
view(man_city_shots)


#----- Can get data for single teams at a time: -----#

# SUPER INTERESTING 
team_breakdown <- understat_team_stats_breakdown(team_urls = "https://understat.com/team/Liverpool/2020")
dplyr::glimpse(team_breakdown)
view(team_breakdown)
#----- Or for multiple teams: -----#
# team_urls <- c("https://understat.com/team/Liverpool/2020",
#                "https://understat.com/team/Manchester_City/2020")
# team_breakdown <- understat_team_stats_breakdown(team_urls = team_urls)


#########################################################################

# Player shot location
raheem_sterling_shots <- understat_player_shots(player_url = "https://understat.com/player/618")
dplyr::glimpse(raheem_sterling_shots)
view(raheem_sterling_shots)

# SUPER Interesting
team_players <- understat_team_players_stats(team_url = c("https://understat.com/team/Liverpool/2022", "https://understat.com/team/Manchester_City/2022"))
dplyr::glimpse(team_players)
view(team_players)


