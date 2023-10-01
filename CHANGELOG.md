# changelog

1.2.3 - 2023-10-01

- fix: viewlayer when getting camera

1.2.2 - 2021-07-24

- fix: problem if forlder is specified but not exists

1.2.1 - 2021-07-24

- code: cleanup, scene properies to property group
- code: created changelog file

1.2.0 - 2020-10-09

- add option to use blender filename

1.1.1 - 2020-03-03

- add camera collection masking option

1.1.0 - 2020-03-03

- new button to make a "true" render from view (Create a cam with same name as the file cans place it in a "quick_cams" collections)
    - opt for later : "only cam" or "no render" (appear, or enable when you tick, "create cam") just create the cam
    - opt for later : "use cam name" if already in cam, output the name of the cam ? (with suffixes...)
- User preferences for defaults values (default placeholder, date format, auto-padding, name normalization)

1.0.3 - 2020-02-11

- fix open folder bug
- removed openGl render though cam button, appears in solid mode only with aview_context False :  
render.opengl(animation=False, sequencer=False, write_still=True, view_context=False)