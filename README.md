A site to encourage me to actually get on and do stuff.

Installation:
Tested on Ubuntu 14.04.
Requires: git, python3, virtualenv
1. git clone https://github.com/geokala/turkey.git
2. cd turkey
3. virtualenv . --python=python3
4. . bin/activate
5. pip install -r requirements.txt

Running:
Tested on Ubuntu 14.04.
From turkey dir created during installation (not turkey/turkey).
1. . bin/activate
2. ./manage.py runserver

Usage:
Access on localhost:5000
Click register to register (you don't have to verify your e-mail address currently). Note that under the current version it's not really multi-user- all tasks will be usable by all users. Not secure. This will change soon.
Login after registering.
Create goals, optionally with subgoals.
Under each goal, create tasks.
Tasks are intended to be performed daily on the current version- little (or lots) and often.
When you have created tasks they will appear on the home screen in orange (if you haven't completed them today) and can be clicked on to complete them (optionally with a comment that will be visible soon). Once completed, they will turn blue for the remainder of the day. You may need to refresh the following day if you still have the page open.
Tracking of success rates, and possibly metrics, coming soon.

Most is under a BSD 3-clause license.
jQuery, bootstrap-growl, and Twitter's Bootstrap are used under the MIT license.
bootstrap-datepicker is used under the Apache Public License.

jQuery: http://jquery.com
bootstrap-growl: http://bootstrap-growl.remabledesigns.com/
Bootstrap: http://getbootstrap.com
Bootstrap-datepicker: https://github.com/eternicode/bootstrap-datepicker
