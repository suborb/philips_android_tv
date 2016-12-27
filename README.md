# philips_android_tv
Tools to control Philips 2016 Android TVs

The API is I suspect the same as JointSpace (http://jointspace.sourceforge.net/) with the following
differences:

* Uses HTTPS over port 1926
* Uses /6/ instead of /1/ as the API path
* All calls have to have digest auth to be successful
* An initial pairing to determine the user/pass is required

The tool here will do the initial pairing. The credentials can then be used in a standard way
(digest) in other tools.
