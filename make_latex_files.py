from program_maker import structure, latex_convert

sessions_csv='ESCoP2017_sessions.csv'
authors_csv="ESCoP2017_subsumed_authors.csv"

escop = structure.Conference(sessions_csv, authors_csv)
latex_convert.contribution_list(escop, filename="contribution_overview.incl.tex")
latex_convert.abstracts(escop, filename="abstracts.incl.tex", write_index=True)
latex_convert.overview_table_code(escop, filename="overview.incl.tex")
