from unicode_tex import tex_args


def create_overview(conference, filename):
    # coference: conference_structure.Conference

    txt = u"%%%% CONTRIBUTION OVERVIEW"
    for d in conference.get_days():
        txt += u"\n\n\\newday{" + str(d) + " Spetember 2017}\n"
        for t in conference.get_times(d):
            newtime_begin_required = True

            for r in conference.get_rooms(d, t):
                session = conference.get_session(d, t, r)
                endtime = conference.get_latest_end_time(d, t)
                if newtime_begin_required:
                    if session.type == "poster":
                        txt += u"\n\\newtimebegin" + tex_args(t, endtime, session.title[:16]) + "\n"
                    else:
                        txt += u"\n\\newtimebegin" + tex_args(t, endtime, "Spoken Session") + "\n"
                    newtime_begin_required = False

                if session.type == "poster":
                    txt += u"\\postersessionstart{}\n"
                else:
                    if session.type == "symposium":
                        tmp= "Symposium: " + session.title
                    else:
                        tmp = session.title
                    txt += u"\n\\talksessionstart" + tex_args(tmp, session.smallest_conf_id,
                                                              session.largets_conf_id, session.room) +"\n"



                if (True):
                    for c in session.contributions:
                        if c.type == "poster":
                            txt += u"    \\postershort" + tex_args(c.conf_id,
                                                c.formated_authors(fullnames=False, first_name_initials=False),
                                                                   c.title) +"\n"
                        else:
                            txt += u"    \\talkshort" + tex_args(c.conf_id, c.start_str,
                                                c.formated_authors(fullnames=False, first_name_initials=False),
                                                                                      c.title, c.end_str) + "\n"
                txt += u"\sessionend{}\n\n"

            txt += u"\n\\newtimeend{}\n"


    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))

