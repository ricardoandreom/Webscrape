library(worldfootballR)
library(tidyverse)
library(xlsx)
library(dplyr)  

####################################

# xG league teams
epl_team_xg_2021 <- fotmob_get_season_stats(
  country = "ENG",
  league_name = "Premier League",
  season_name = "2020/2021",
  stat_name = "Expected goals",
  team_or_player = "team"
)

epl_team_xg_2021 %>%
  dplyr::select(
    league_id,
    league_name,
    season_id,
    season_name,
    team_id,
    team_name = participant_name,
    matches_played,
    xg = stat_value,
    g = sub_stat_value
  ) %>%
  dplyr::glimpse()


# stats xG pl per team
stats_pl<-fotmob_get_season_stats(
  league_id = 47,
  season_name = "2020/2021",
  stat_name = "Expected goals",
  team_or_player = "team"
)


##################################

# xG teams - several countries
team_xgs_2021 <- fotmob_get_season_stats(
  country =        c("ITA",     "ESP"),
  league_name =    c("Serie A", "LaLiga"),
  season_name =    c("2020/2021", "2021/2022"),
  stat_name =      c("Expected goals", "xG conceded"),
  team_or_player = "team"
)

## 2 leagues x 20 teams x 2 seasons x 2 stats = 160 rows
team_xgs_2021 %>% nrow()
view(team_xgs_2021)


###############################################

# xG teams - ucl
ucl_xg <- fotmob_get_season_stats(
    league_id = 42,
    season_name = "2020/2021",
    stat_name = "Expected goals",
    team_or_player = "team"
  )
view(ucl_xg)


###################################################

# Player stats

epl_player_xg_2021 <- fotmob_get_season_stats(
  country = "ENG",
  league_name = "Premier League",
  season = "2020/2021",
  stat_name = "Expected goals (xG)",
  team_or_player = "player"
)

epl_player_xg_2021 %>%
  dplyr::select(
    league_id,
    league_name,
    season_id,
    season_name,
    team_id,
    ## NOTE: particiant_id is a typo on behalf of fotmob! We leave it as is.
    player_id = particiant_id,
    player_name = participant_name,
    minutes_played,
    matches_played,
    xg = stat_value,
    g = sub_stat_value
  ) %>%
  dplyr::glimpse()

view(epl_player_xg_2021)


#################################################################################

# match league scores
league_matches <- fotmob_get_league_matches(
  country =     c("ENG",            "ESP"   ),
  league_name = c("Premier League", "LaLiga")
)

league_matches_unnested <- league_matches %>%
  dplyr::select(match_id = id, home, away) %>%
  tidyr::unnest_wider(c(home, away), names_sep = "_")
dplyr::glimpse(league_matches_unnested)

view(league_matches_unnested)

##################################################################################

results <- fotmob_get_matches_by_date(date = c("20210925", "20210926"))
dplyr::glimpse(results)

##################################################################################

# League tables

league_tables <- fotmob_get_league_tables(
  country =     c("ENG",            "ESP"   ),
  league_name = c("Premier League", "LaLiga")
)
# or
# league_tables <- fotmob_get_league_tables(league_id = c(47, 87))


# tabela só com dados dos jogos fora das equipas
away_league_tables <- league_tables %>%
  dplyr::filter(table_type == "away")
dplyr::glimpse(away_league_tables)

home_league_tables <- league_tables %>%
  dplyr::filter(table_type == "home")
dplyr::glimpse(away_league_tables)

view(league_tables)
view(away_league_tables)

################################################################################

# MATCH LEVEL STATS

fotmob_matches <- c(3609994, 3610132)
match_info <- fotmob_get_match_info(fotmob_matches)
match_info %>%
  dplyr::select(match_id, match_date_date_formatted:dplyr::last_col()) %>%
  dplyr::glimpse()

# tem info sobre attendance do jogo
view(match_info)


###############################################################################

# match team stats

match_team_stats <- fotmob_get_match_team_stats(fotmob_matches)
match_team_stats %>%
  dplyr::select(match_id, title:dplyr::last_col()) %>%
  dplyr::glimpse()


match_team_stats %>%
  dplyr::filter(match_id == dplyr::first(match_id)) %>%
  dplyr::count(title)

view(match_team_stats)


##############################################

# Match Shooting Locations

# referentes aos jogos fotmob matches
match_details <- fotmob_get_match_details(fotmob_matches)
dplyr::glimpse(match_details)
view(match_details)

##################################################

# PLAYERS

# player stats dos jogadores dos jogos fotmob_matches
players <- fotmob_get_match_players(fotmob_matches)
dplyr::glimpse(players)

view(players)

# stats só de um jogador do jogo anterior

salah <- players %>% dplyr::filter(id == "292462")
salah_shotmap <- salah %>% 
  dplyr::select(player_id = id, shotmap) %>% 
  tidyr::unnest(shotmap)
dplyr::glimpse(salah_shotmap)

view(salah)

# shot map de um jogador num jogo
view(salah_shotmap)

# outras stats do salah num jogos(s)
salah_stats <- salah %>% 
  dplyr::select(player_id = id, tidyselect::vars_select_helpers$starts_with("stats_")) %>% 
  janitor::remove_empty(which = "cols")
dplyr::glimpse(salah_stats)

view(salah_stats)
