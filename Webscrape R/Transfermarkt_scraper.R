library(worldfootballR)

####################################################
mapped_players <- player_dictionary_mapping()
dplyr::glimpse(mapped_players)
view(mapped_players)
##################################################

team_urls <- tm_league_team_urls(country_name = "England", start_year = 2020)
# if it's not a league in the stored leagues data in worldfootballR_data repo:
league_one_teams <- tm_league_team_urls(start_year = 2020, league_url = "https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3")

##################################################################################

# players urls from a particular team
tm_team_player_urls(team_url = "https://www.transfermarkt.com/fc-burnley/startseite/verein/1132/saison_id/2020")

##############################################################################


# get a list of team URLs for the EPL 2021/22 season
epl_teams <- tm_league_team_urls(country_name = "England", start_year = 2021)
# get all EPL managers for the 2021/22 season
epl_managers <- tm_team_staff_urls(team_urls = epl_teams, staff_role = "Manager")

# get all EPL goal keeping coaches for the 2021/22 season
epl_gk_coaches <- tm_team_staff_urls(team_urls = epl_teams, staff_role = "Goalkeeping Coach")
view(epl_gk_coaches)

######################################################################################

#----- to get the EPL table after matchday 1 of the 20/21 season: -----#
epl_matchday_1_table <- tm_matchday_table(country_name="England", start_year="2020", matchday=1)
dplyr::glimpse(epl_matchday_1_table)

# #----- to get the EPL table after each matchdays from matchday 1 to matchday 35 of the 20/21 season: -----#
# epl_matchday_1to35_table <- tm_matchday_table(country_name="England", start_year="2020", matchday=c(1:35))

#----- to get the League One table after each matchdays from matchday 1 to matchday 5 of the 20/21 season: -----#
league_one_matchday_1_table <- tm_matchday_table(start_year="2020", matchday=1:5,
                                                 league_url="https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3")
dplyr::glimpse(league_one_matchday_1_table)

###############################################################################################


# Laliga players making their LaLiga debut in 2021/2022
laliga_debutants <- tm_league_debutants(country_name = "Spain", debut_type = "league", debut_start_year = 2021, debut_end_year = 2021)
dplyr::glimpse(laliga_debutants)

# English League One players making their PRO debuts in 2021/2022
league_one_PRO_debutants <- tm_league_debutants(country_name = "", league_url = "https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3", debut_type = "pro", debut_start_year = 2021, debut_end_year = 2021)
dplyr::glimpse(league_one_PRO_debutants)

view(laliga_debutants)

##############################################################################

#----- LaLiga players with expiring contracts in 2022: -----#
laliga_expiring <- tm_expiring_contracts(country_name = "Spain", contract_end_year = 2023)
dplyr::glimpse(laliga_expiring)
view(laliga_expiring)
#----- Can even do it for non-standard leagues - English League One players with expiring contracts in 2022: -----#
# league_one_expiring <- tm_expiring_contracts(country_name = "",
#                                                contract_end_year = 2023,
#                                                league_url = "https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3")


#####################################################################################

# to get all current injuries for LaLiga
laliga_injuries <- tm_league_injuries(country_name = "Spain")
dplyr::glimpse(laliga_injuries)

#----- Can even do it for non-standard leagues - get all current injuries for League One in England
# league_one_injuries <- tm_league_injuries(country_name = "",
#                                                league_url = "https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3")
view(laliga_injuries)
#######################################################################################


#----- for one team: -----#
bayern <- tm_team_transfers(team_url = "https://www.transfermarkt.com/fc-bayern-munchen/startseite/verein/27/saison_id/2020", transfer_window = "all")
dplyr::glimpse(bayern)
view(bayern)
#----- or for multiple teams: -----#
# team_urls <- tm_league_team_urls(country_name = "England", start_year = 2020)
# epl_xfers_2020 <- tm_team_transfers(team_url = team_urls, transfer_window = "all")


#####################################################################################


# basic player team stats
bayern <- tm_squad_stats(team_url = "https://www.transfermarkt.com/fc-bayern-munchen/startseite/verein/27/saison_id/2020")
dplyr::glimpse(bayern)
view(bayern)
######################################################################################


#----- Can do it for a single league: -----#
a_league_valuations <- tm_player_market_values(country_name = "Portugal",
                                               start_year = 2022)
dplyr::glimpse(a_league_valuations)
view(a_league_valuations)

#----- Can also do it for multiple leagues: -----#
# big_5_valuations <- tm_player_market_values(country_name = c("England", "Spain", "France", "Italy", "Germany"),
#                                        start_year = 2021)



################################################################################


#----- for a single player: -----#
hazard_injuries <- tm_player_injury_history(player_urls = "https://www.transfermarkt.com/eden-hazard/profil/spieler/50202")
dplyr::glimpse(hazard_injuries)

#----- for multiple players: -----#
# # can make use of a tm helper function:
# burnley_player_urls <- tm_team_player_urls(team_url = "https://www.transfermarkt.com/fc-burnley/startseite/verein/1132/saison_id/2021")
# # then pass all those URLs to the tm_player_bio
# burnley_player_injuries <- tm_player_injury_history(player_urls = burnley_player_urls)


###############################################################################

# get a list of team URLs for the EPL 2021/22 season
epl_teams <- tm_league_team_urls(country_name = "England", start_year = 2021)
#----- then use the URLs to pass to the function, and select the role you wish to see results for: -----#
club_manager_history <- tm_team_staff_history(team_urls = epl_teams, staff_role = "Manager")
dplyr::glimpse(club_manager_history)

#----- can also get other roles: -----#
# club_caretaker_manager_history <- tm_team_staff_history(team_urls = epl_teams, staff_role = "Caretaker Manager")

################################################################################


# get a list of team URLs for the EPL 2021/22 season
# epl_teams <- tm_league_team_urls(country_name = "England", start_year = 2021)

# get all EPL goal keeping coaches for the 2021/22 season
epl_gk_coaches <- tm_team_staff_urls(team_urls = epl_teams[1:3], staff_role = "Goalkeeping Coach")

# then you can pass these URLs to the function and get job histories for the selected staff members
epl_gk_coach_job_histories <- tm_staff_job_history(staff_urls = epl_gk_coaches)
dplyr::glimpse(epl_gk_coach_job_histories)

#----- Can also do it for non standard leagues: -----#
# league_one_valuations <- tm_player_market_values(country_name = "",
#                                        start_year = 2021,
#                                        league_url = "https://www.transfermarkt.com/league-one/startseite/wettbewerb/GB3")