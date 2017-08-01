# poster session have no end time


from program_maker import structure,  latex_convert


filename="contribution_overview.incl.tex"
sessions_csv='ESCoP2017_sessions.csv'
authors_csv="ESCoP2017_subsumed_authors.csv"

escop = structure.Conference(sessions_csv, authors_csv)

latex_convert.create_overview(escop, filename)

