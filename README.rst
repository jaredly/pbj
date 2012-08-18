Python Build Jelly

**New**

just added zsh completion! found in the file ``zsh.sugar``

Anyway, PBJ is a simple, extensible pythonic build framework, whose purpose is to be dead simple for the basic cases.

Here's an example::

   from pbj import Builder, cmd
   import os
   
   build = Builder("PJs")

   build.cmd("jstest", ("js", "test/runtests.js"))
   build.clean("build", "test/py/*.js")

   @build.file("build/pjslib.js", depends="jslib/*.js")
   def jslib(name):
       text = cmd("cat", "jslib/*.js")
       if not os.path.exists("build"):
           os.mkdir("build")
       open("build/pjslib.js").write(text)

   if __name__ == "__main__":
       build.run()

Cool things: targets are classes, and decorate functions.

And...this project is just starting out, so I'll fill the rest in later.

Cheers.
