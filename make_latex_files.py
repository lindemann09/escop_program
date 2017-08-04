from program_maker import structure, latex_convert

sessions_csv='ESCoP2017_sessions.csv'
escop = structure.Conference(sessions_csv)

latex_convert.contribution_list(escop, filename="contributions.incl.tex", talks_first=True)
latex_convert.abstracts(escop, filename="abstracts.incl.tex", write_index=True)
latex_convert.overview_table_code(escop, filename="overview.incl.tex")

print("copy this files to your escop_tex folder")
