library(worldfootballR)


######################################### obter a info de competições de seleções

# Exemplos
# podemos filtrar por ano, ronda, país e género

wc_2018_urls <- get_match_urls(country = "", gender = "M", season_end_year = 2018, tier = "", non_dom_league_url = "https://fbref.com/en/comps/1/history/World-Cup-Seasons")

friendly_int_2021_urls <- get_match_urls(country = "", gender = "M", season_end_year = 2021, tier = "", non_dom_league_url = "https://fbref.com/en/comps/218/history/Friendlies-M-Seasons")

euro_2021_urls <- get_match_urls(country = "", gender = "M", season_end_year = 2021, tier = "", non_dom_league_url = "https://fbref.com/en/comps/676/history/European-Championship-Seasons")

copa_2019_urls <- get_match_urls(country = "", gender = "M", season_end_year = 2019, tier = "", non_dom_league_url = "https://fbref.com/en/comps/685/history/Copa-America-Seasons")

#####################################

#   GET MATCH INFO RESULTS

# euro 2016 results
euro_2016_results <- get_match_results(country = "", gender = "M", season_end_year = 2016, tier = "", non_dom_league_url = "https://fbref.com/en/comps/676/history/European-Championship-Seasons")

# 2019 Copa America results:
copa_2019_results <- get_match_results(country = "", gender = "M", season_end_year = 2019, non_dom_league_url = "https://fbref.com/en/comps/685/history/Copa-America-Seasons")

# for international friendlies:
international_results <- get_match_results(country = "", gender = "M", season_end_year = 2021, tier = "", non_dom_league_url = "https://fbref.com/en/comps/218/history/Friendlies-M-Seasons")

################################################################################

#    Get match report

# function to extract match report data for 2018 world cup
wc_2018_report <- get_match_report(match_url = wc_2018_urls)
# function to extract match report data for 2021 international friendlies
friendlies_report <- get_match_report(match_url = friendly_int_2021_urls)

###########################################################################################

# GET MATCH LINEUPS

# function to extract match lineups and some player statistics for each game
copa_2019_lineups <- get_match_lineups(match_url = copa_2019_urls) 

#######################################################################################

#           Get shooting and shot creation events

shots_wc_2018 <- get_match_shooting(wc_2018_urls)

###########################################################################################

# GET ADVANCED STATISTICS

# posso filtrar por equipa e por jogador

# por jogador
advanced_match_stats_player <- get_advanced_match_stats(match_url = wc_2018_urls, stat_type = "possession", team_or_player = "player")

#por seleção
advanced_match_stats_team <- get_advanced_match_stats(match_url = wc_2018_urls, stat_type = "passing_types", team_or_player = "team")

'''

STATS disponíveis
summary
passing
passing_types
defense
possession
misc
keeper
'''