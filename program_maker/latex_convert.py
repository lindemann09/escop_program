from unicode_tex import tex_args, unicode_to_tex


# helper
def plain_name(surname_comma_first_name):
    # converts <surname>, <fist name> to <fist name> <surname>
    x = surname_comma_first_name.split(',')
    return x[1].strip() + " " + x[0].strip()

def punctuation(txt):
    # adds punctuation mark at the end, if has none alreay

    if txt[-1] not in u"!#%&()*+,-.:;=?":
        return txt + "."
    return txt


def create_overview(conference, filename):
    # conference: conference_structure.Conference

    txt = u"%%%% CONTRIBUTION OVERVIEW"
    for d in conference.get_day_ids():
        weekday = conference.get_all_sessions_at_day(d)[0].weekday
        txt += u"\n\n\\overviewdaybegin{" + weekday + ", " + str(d) + " September 2017}\n"
        for t in conference.get_times(d):
            newtime_begin_required = True

            for r in conference.get_rooms(d, t):
                session = conference.get_session(d, t, r)
                if newtime_begin_required:
                    if session.type == "poster":
                        txt += u"\n\\overviewtimeslotbegin" + tex_args(t, session.end_str,
                                session.title[:session.title.find("-")].strip()) + "\n"
                    else:
                        txt += u"\n\\overviewtimeslotbegin" + tex_args(t, session.end_str, "Spoken Session") + "\n"
                    newtime_begin_required = False

                if session.type == "poster":
                    txt += u"\\overiewposterbegin{}\n"
                else:
                    if session.type == "symposium":
                        type_txt = "Symposium"
                        if len(session.chair) > 0:
                            info_code = u"{\\newline\\itshape{Organized by " + unicode_to_tex(plain_name(session.chair)) + u"}}"
                        else:
                            info_code = u"{}"
                    else:
                        type_txt = ""
                        if len(session.chair) > 0:
                            info_code = u"{\\newline\\itshape{Chaired by " + unicode_to_tex(plain_name(session.chair)) + u"}}"
                        else:
                            info_code = u"{}"

                    txt += u"\n\\overiewsessionbegin" + tex_args(u"{}-{}".format(session.smallest_conf_id, session.largets_conf_id),
                                                                 type_txt, session.room,
                                                                 session.title) + info_code +"\n"

                if (True):
                    for c in session.contributions:
                        if c.type == "poster":
                            txt += u"    \\postershort" + tex_args(c.conf_id,
                                                c.formated_authors(fullnames=False, first_name_initials=False),
                                                                   punctuation(c.title)) +"\n"
                        else:
                            txt += u"    \\talkshort" + tex_args(c.conf_id, c.start_str, c.end_str,
                                                c.formated_authors(fullnames=False, first_name_initials=False),
                                                                 punctuation(c.title)) + "\n"
                txt += u"\overiewsessionend{}\n\n"

            txt += u"\n\\overviewtimeslotend{}\n"
        txt += u"\n\n\\overviewdayend{}\n"


    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))



def create_abstracts(conference, filename, write_index=False):
    # conference: conference_structure.Conference
    #FIXME emails?

    poster = u""
    talks = u""

    for d in conference.get_day_ids():
        for session in conference.get_all_sessions_at_day(d):
            txt = u""
            session_time = u"{0}, {1}-{2}".format(session.weekday, session.start_str, session.end_str)

            if session.type == "poster":
                txt += u"\n\\abstractposterbegin" + tex_args(session_time, session.room,
                                                               session.title[:session.title.find("-")].strip()) + "\n"
            else:
                if session.type == "symposium":
                    tmp = "Symposium: " + session.title
                else:
                    tmp = session.title
                txt += u"\n\\abstractsessionbegin" + tex_args(session_time,session.room, tmp) + "\n" #FIXME chair

            for c in session.contributions:
                if session.type == "poster":
                    start_time = ""
                else:
                    start_time = u"{0}-{1}".format(c.start_str, c.end_str)
                txt += u"    \\escopabstract" + tex_args(c.conf_id, start_time) + \
                                        u"{" + c.formated_authors(fullnames=True, first_name_initials=False,
                                                                  affiliation_ids=True,
                                                                  orga_id_format=u"$^{{{0}}}$",
                                                                  tex_code=True,
                                                                  write_index=write_index) + u"}" + \
                                        u"{" + c.formated_organisations(orga_id_format=u"$^{{{0}}}$", tex_code=True) + u"}" + \
                                        tex_args(c.title, c.abstract, c.first_author_email) + "\n\n"

            txt += u"\\abstractsessionend{}\n\n"
            if session.type == "poster":
                poster += txt
            else:
                talks += txt

    txt = u"%%%% ABSTRACTS" + talks + poster
    print("writing: " + filename)
    with open(filename, "wb") as f:
       f.write(txt.encode("UTF-8"))

