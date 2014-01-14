#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2013             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

register_rulegroup("activechecks",
    _("Active checks (HTTP, TCP, etc.)"),
    _("Configure active networking checks like HTTP and TCP"))
group = "activechecks"

# This elements are also used in check_parameters.py
check_icmp_params = [
   ( "rta",
     Tuple(
         title = _("Round trip average"),
         elements = [
             Float(title = _("Warning if above"), unit = "ms", default_value = 200.0),
             Float(title = _("Critical if above"), unit = "ms", default_value = 500.0),
         ])),
   ( "loss",
     Tuple(
         title = _("Packet loss"),
         help = _("When the percentual number of lost packets is equal or greater then "
                  "the level, then the according state is triggered. The default for critical "
                  "is 100%. That means that the check is only critical if <b>all</b> packets "
                  "are lost."),
         elements = [
             Percentage(title = _("Warning if above"), default_value = 80.0),
             Percentage(title = _("Critical if above"), default_value = 100.0),
         ])),

    ( "packets",
      Integer(
          title = _("Number of packets"),
          help = _("Number ICMP echo request packets to send to the target host on each "
                   "check execution. All packets are sent directly on check execution. Afterwards "
                   "the check waits for the incoming packets."),
          minvalue = 1,
          maxvalue = 20,
          default_value = 5,
       )),

     ( "timeout",
       Integer(
           title = _("Total timeout of check"),
           help = _("After this time (in seconds) the check is aborted, regardless "
                    "of how many packets have been received yet."),
           minvalue = 1,
       )),
]


register_rule(group,
    "active_checks:icmp",
    Dictionary(
        title = _("Check hosts with PING (ICMP Echo Request)"),
        help = _("This ruleset allows you to configure explicit PING monitoring of hosts. "
                 "Usually a PING is being used as a host check, so this is not neccessary. "
                 "There are some situations, however, where this can be useful. One of them "
                 "is when using the Check_MK Micro Core with SMART Ping and you want to "
                 "track performance data of the PING to some hosts, nevertheless."),
        elements = [
           ( "description",
             TextUnicode(
                 title = _("Service Description"),
                 allow_empty = False,
                 default_value = "PING",
           ))
        ] + check_icmp_params,
        match = "all",
    )
)

register_rule(group,
    "active_checks:ftp",
    Transform(
        Dictionary(
            elements = [
                ( "response_time",
                  Tuple(
                      title = _("Expected response time"),
                      elements = [
                          Float(
                              title = _("Warning if above"),
                              unit = "ms",
                              default_value = 100.0),
                          Float(
                              title = _("Critical if above"),
                              unit = "ms",
                              default_value = 200.0),
                      ])
                 ),
                 ( "timeout",
                   Integer(
                       title = _("Seconds before connection times out"),
                       unit = _("sec"),
                       default_value = 10,
                   )
                 ),
                 ( "refuse_state",
                   DropdownChoice(
                       title = _("State for connection refusal"),
                       choices = [ ('crit', _("CRITICAL")),
                                   ('warn', _("WARNING")),
                                   ('ok',   _("OK")),
                                 ])
                 ),

                 ( "send_string",
                   TextAscii(
                       title = _("String to send"),
                       size = 30)
                 ),
                 ( "expect",
                   ListOfStrings(
                       title = _("Strings to expect in response"),
                       orientation = "horizontal",
                       valuespec = TextAscii(size = 30),
                   )
                 ),

                 ( "ssl",
                   FixedValue(
                       value = True,
                       totext = _("use SSL"),
                       title = _("Use SSL for the connection."))

                 ),
                 ( "cert_days",
                   Integer(
                       title = _("SSL certificate validation"),
                       help = _("Minimum number of days a certificate has to be valid"),
                       unit = _("days"),
                       default_value = 30)
                 ),
            ]),
            forth = lambda x: type(x) == tuple and x[1] or x,
            title = _("Check FTP Service"),
        )
)


register_rule(group,
    "active_checks:dns",
    Tuple(
        title = _("Check DNS service"),
        help = _("Check the resolution of a hostname into an IP address by a DNS server. "
                 "This check uses <tt>check_dns</tt> from the standard Nagios plugins."),
        elements = [
           TextAscii(title = _("Hostname"), allow_empty = False,
                     help = _('The name or address you want to query')),
           Dictionary(
               title = _("Optional parameters"),
               elements = [
                   ( "server",
                     TextAscii(
                         title = _("DNS Server"),
                         allow_empty = False,
                         help = _("Optional DNS server you want to use for the lookup"))),
                   ( "expected_address",
                     TextAscii(
                         title = _("Expected Address"),
                         allow_empty = False,
                         help = _("Optional IP-Address you expect the DNS server to return. The host "
                                  "must end with a dot (.) " )),
                   ),
                   ( "expected_authority",
                     FixedValue(
                         value  = True,
                         title  = _("Expect Authoritative DNS Server"),
                         totext = _("Expect Authoritative"),
                         help   = _("Optional expect the DNS server to be authoriative"
                                    "for the lookup ")),
                   ),
                   ( "response_time",
                     Tuple(
                         title = _("Expected response time"),
                         elements = [
                             Float(
                                 title = _("Warning if above"),
                                 unit = "sec",
                                 default_value = 1),
                             Float(
                                 title = _("Critical if above"),
                                 unit = "sec",
                                 default_value = 2),
                         ])
                    ),
                   ( "timeout",
                      Integer(
                          title = _("Seconds before connection times out"),
                          unit = _("sec"),
                          default_value = 10,
                      )
                    ),
                ]),
        ]
    ),
    match = 'all')

register_rule(group,
    "active_checks:sql",
    Dictionary(
        title = _("Check SQL Database"),
        help = _("This check connects to the specified database, sends a custom SQL-statement "
                 "or starts a procedure, and checks that the result has a defined format "
                 "containing three columns, a number, a text, and performance data. Upper or "
                 "lower levels may be defined here.  If they are not defined the number is taken "
                 "as the state of the check.  If a procedure is used, input parameters of the "
                 "procedures may by given as comma separated list. "
                 "This check uses the active check <tt>check_sql</tt>."),
        optional_keys = [ "levels", "levels_low", "perfdata", "port", "procedure" ],
        elements = [
            ( "description",
              TextUnicode(title = _("Service Description"),
                 help = _("The name of this active service to be displayed."),
                 allow_empty = False,
            )),
            ( "dbms",
               DropdownChoice(
                   title = _("Type of Database"),
                   choices = [
                      ( "mysql",    _("MySQL") ),
                      ( "postgres", _("PostgreSQL") ),
                      ( "mssql", _("MSSQL") ),
                      ( "oracle",   _("Oracle") ),
                   ],
                   default_value = "postgres",
               ),
            ),
            ( "port",
               Integer(title = _("Database Port"), allow_empty = True,
                      help = _('The port the DBMS listens to'))
            ),
            ( "name",
               TextAscii(title = _("Database Name"), allow_empty = False,
                      help = _('The name of the database on the DBMS'))
            ),
            ( "user",
               TextAscii(title = _("Database User"), allow_empty = False,
                      help = _('The username used to connect to the database'))
            ),
            ( "password",
               Password(title = _("Database Password"), allow_empty = False,
                      help = _('The password used to connect to the database'))
            ),
            ( "sql",
              TextAscii(title = _("SQL-statement or procedure name"), allow_empty = False,
                      help = _('The SQL-statement or procedure name which is executed on the DBMS'))
            ),
            ( "procedure",
            Dictionary(
                optional_keys = [ "input" ],
                title = _("Use procedure call instead of sql statement"),
                help = _("If you activate this option, a name of a stored "
                    "procedure is used instead of an SQL statement. "
                    "The procedure should return one output variable, "
                    "which is evaluated in the check. If input parameters "
                    "are required, they may be specified below."),
                elements = [
                        ("useprocs",
                        FixedValue(
                            value = True,
                            totext = _("procedure call is used"),
                        )),
                        ("input",
                        TextAscii(
                            title = _("Input Parameters"),
                            allow_empty = True,
                            help = _("Input parameters, if required by the database procedure. "
                                     "If several parameters are required, use commas to separate them."),
                        )),
                    ]
                ),
            ),
            ( "levels",
            Tuple(
                title = _("Upper levels for first output item"),
                elements = [
                    Float( title = _("Warning if above")),
                    Float( title = _("Critical if above"))
                ])
            ),
            ( "levels_low",
            Tuple(
                title = _("Lower levels for first output item"),
                elements = [
                    Float( title = _("Warning if below")),
                    Float( title = _("Critical if below"))
                ])
            ),
            ( "perfdata",
              FixedValue(True, totext=_("Store output value into RRD database"), title = _("Performance Data"), ),
            )
        ]
    ),
    match = 'all')

register_rule(group,
    "active_checks:tcp",
    Tuple(
        title = _("Check connecting to a TCP port"),
        help = _("This check tests the connection to a TCP port. It uses "
                 "<tt>check_tcp</tt> from the standard Nagios plugins."),
        elements = [
           Integer(title = _("TCP Port"), minvalue=1, maxvalue=65535),
           Dictionary(
               title = _("Optional parameters"),
               elements = [
                   ( "svc_description",
                     TextUnicode(
                         title = _("Service description"),
                         allow_empty = False,
                         help = _("Here you can specify a service description. "
                                  "If this parameter is not set, the service is named <tt>TCP Port {Portnumber}</tt>"))),
                   ( "hostname",
                     TextAscii(
                         title = _("DNS Hostname"),
                         allow_empty = False,
                         help = _("If you specify a hostname here, then a dynamic DNS lookup "
                                  "will be done instead of using the IP address of the host "
                                  "as configured in your host properties."))),
                   ( "response_time",
                     Tuple(
                         title = _("Expected response time"),
                         elements = [
                             Float(
                                 title = _("Warning if above"),
                                 unit = "ms",
                                 default_value = 100.0),
                             Float(
                                 title = _("Critical if above"),
                                 unit = "ms",
                                 default_value = 200.0),
                         ])
                    ),
                    ( "timeout",
                      Integer(
                          title = _("Seconds before connection times out"),
                          unit = _("sec"),
                          default_value = 10,
                      )
                    ),
                    ( "refuse_state",
                      DropdownChoice(
                          title = _("State for connection refusal"),
                          choices = [ ('crit', _("CRITICAL")),
                                      ('warn', _("WARNING")),
                                      ('ok',   _("OK")),
                                    ])
                    ),

                    ( "send_string",
                      TextAscii(
                          title = _("String to send"),
                          size = 30)
                    ),
                    ( "escape_send_string",
                      FixedValue(
                          value = True,
                          title = _("Expand <tt>\\n</tt>, <tt>\\r</tt> and <tt>\\t</tt> in the sent string"),
                          totext = _("expand escapes"))
                    ),
                    ( "expect",
                      ListOfStrings(
                          title = _("Strings to expect in response"),
                          orientation = "horizontal",
                          valuespec = TextAscii(size = 30),
                      )
                    ),
                    ( "expect_all",
                      FixedValue(
                          value = True,
                          totext = _("expect all"),
                          title = _("Expect <b>all</b> of those strings in the response"))
                    ),
                    ( "jail",
                      FixedValue(
                          value = True,
                          title = _("Hide response from socket"),
                          help = _("As soon as you configure expected strings in "
                                   "the response the check will output the response - "
                                   "as long as you do not hide it with this option"),
                          totext = _("hide response"))
                    ),
                    ( "mismatch_state",
                      DropdownChoice(
                          title = _("State for expected string mismatch"),
                          choices = [ ('crit', _("CRITICAL")),
                                      ('warn', _("WARNING")),
                                      ('ok',   _("OK")),
                                    ])
                    ),
                    ( "delay",
                      Integer(
                          title = _("Seconds to wait before polling"),
                          help = _("Seconds to wait between sending string and polling for response"),
                          unit = _("sec"),
                          default_value = 0,
                      )
                    ),
                    ( "maxbytes",
                      Integer(
                          title = _("Maximum number of bytes to receive"),
                          help = _("Close connection once more than this number of "
                                   "bytes are received. Per default the number of "
                                   "read bytes is not limited. This setting is only "
                                   "used if you expect strings in the response."),
                          default_value = 1024,
                      ),
                    ),

                    ( "ssl",
                      FixedValue(
                          value = True,
                          totext = _("use SSL"),
                          title = _("Use SSL for the connection."))

                    ),
                    ( "cert_days",
                      Integer(
                          title = _("SSL certificate validation"),
                          help = _("Minimum number of days a certificate has to be valid"),
                          unit = _("days"),
                          default_value = 30)
                    ),

                    ( "quit_string",
                      TextAscii(
                          title = _("Final string to send"),
                          help = _("String to send server to initiate a clean close of "
                                   "the connection"),
                          size = 30)
                    ),
                ]),
        ]
    ),
    match = 'all')


register_rule(group,
    "active_checks:http",
    Tuple(
        title = _("Check HTTP service"),
        help = _("Check HTTP/HTTPS service using the plugin <tt>check_http</tt> "
                 "from the standard Nagios Plugins. "
                 "This plugin tests the HTTP service on the specified host. "
                 "It can test normal (HTTP) and secure (HTTPS) servers, follow "
                 "redirects, search for strings and regular expressions, check "
                 "connection times, and report on certificate expiration times. "),
        elements = [
            TextUnicode(
                title = _("Name"),
                help = _("Will be used in the service description. If the name starts with"
                         "a caret (^) the service description will not be prefixed with HTTP." ),
                allow_empty = False),
            Alternative(
                title = _("Mode of the Check"),
                help = _("Perform a check of the URL or the certificate expiration."),
                elements = [
                    Dictionary(
                        title = _("Check the URL"),
                        elements = [
                           ( "virthost",
                             Tuple(
                               title = _("Virtual host"),
                               elements = [
                                 TextAscii(
                                   title = _("Name of the virtual host"),
                                   help = _("Set this in order to specify the name of the "
                                    "virtual host for the query (using HTTP/1.1). When you "
                                    "leave this empty, then the IP address of the host "
                                    "will be used instead."),
                                   allow_empty = False),
                                 Checkbox(
                                    label = _("Omit specifying an IP address"),
                                    help = _("Usually Check_MK will nail this check to the "
                                      "IP address of the host it is attached to. With this "
                                      "option you can have the check use the name of the "
                                      "virtual host instead and do a dynamic DNS lookup."),
                                    true_label = _("omit IP address"),
                                    false_label = _("specify IP address"),
                                  ),
                                ]
                              )
                           ),
                           ( "uri",
                             TextAscii(
                               title = _("URI to fetch (default is <tt>/</tt>)"),
                               allow_empty = False,
                               default_value = "/")
                           ),
                           ( "port",
                             Integer(
                               title = _("TCP Port"),
                               minvalue = 1,
                               maxvalue = 65535,
                               default_value = 80)
                           ),
                           ( "ssl",
                             FixedValue(
                                 value = True,
                                 totext = _("use SSL/HTTPS"),
                                 title = _("Use SSL/HTTPS for the connection."))
                           ),
                           ( "sni",
                             FixedValue(
                                 value = True,
                                 totext = _("enable SNI"),
                                 title = _("Enable SSL/TLS hostname extension support (SNI)"),
                             )
                           ),
                           ( "response_time",
                             Tuple(
                                 title = _("Expected response time"),
                                 elements = [
                                     Float(
                                         title = _("Warning if above"),
                                         unit = "ms",
                                         default_value = 100.0),
                                     Float(
                                         title = _("Critical if above"),
                                         unit = "ms",
                                         default_value = 200.0),
                                 ])
                            ),
                            ( "timeout",
                              Integer(
                                  title = _("Seconds before connection times out"),
                                  unit = _("sec"),
                                  default_value = 10,
                              )
                            ),
                            ( "user_agent",
                              TextAscii(
                                  title = _("User Agent"),
                                  help = _("String to be sent in http header as \"User Agent\""),
                                  allow_empty = False,
                              ),
                            ),
                            ( "add_headers",
                              ListOfStrings(
                                  title = _("Additional header lines"),
                                  orientation = "vertical",
                                  valuespec = TextAscii(size = 40),
                              ),
                            ),
                            ( "auth",
                              Tuple(
                                  title = _("Authorization"),
                                  help = _("Credentials for HTTP Basic Authentication"),
                                  elements = [
                                      TextAscii(
                                          title = _("Username"),
                                          size = 12,
                                          allow_empty = False),
                                      TextAscii(
                                          title = _("Password"),
                                          size = 12,
                                          allow_empty = False),
                                  ])
                            ),
                            ( "proxy_auth",
                              Tuple(
                                  title = _("Proxy-Authorization"),
                                  help = _("Credentials for HTTP Proxy with basic authentication"),
                                  elements = [
                                      TextAscii(
                                          title = _("Username"),
                                          size = 12,
                                          allow_empty = False),
                                      TextAscii(
                                          title = _("Password"),
                                          size = 12,
                                          allow_empty = False),
                                  ])
                            ),
                            ( "onredirect",
                              DropdownChoice(
                                  title = _("How to handle redirect"),
                                  choices = [
                                    ( 'ok',         _("Make check OK") ),
                                    ( 'warning',    _("Make check WARNING") ),
                                    ( 'critical',   _("Make check CRITICAL") ),
                                    ( 'follow',     _("Follow the redirection") ),
                                    ( 'sticky',     _("Follow, but stay to same IP address") ),
                                    ( 'stickyport', _("Follow, but stay to same IP-address and port") ),
                                  ],
                                  default_value = 'follow'),
                            ),
                            ( "expect_response",
                              ListOfStrings(
                                  title = _("Strings to expect in server response"),
                                  help = _("At least one of these strings is expected in "
                                           "the first (status) line of the server response "
                                           "(default: <tt>HTTP/1.</tt>). If specified skips "
                                           "all other status line logic (ex: 3xx, 4xx, 5xx "
                                           "processing)"),
                              )
                            ),
                            ( "expect_string",
                              TextAscii(
                                  title = _("Fixed string to expect in the content"),
                                  allow_empty = False,
                              )
                            ),
                            ( "expect_regex",
                              Transform(
                                Tuple(
                                    orientation = "vertical",
                                    show_titles = False,
                                    elements = [
                                        RegExp(label = _("Regular expression: ")),
                                        Checkbox(label = _("Case insensitive")),
                                        Checkbox(label = _("return CRITICAL if found, OK if not")),
                                        Checkbox(label = _("Multiline string matching")),
                                    ]
                                ),
                                forth = lambda x: len(x) == 3 and tuple(list(x) + [False]) or x,
                                title = _("Regular expression to expect in content"),
                              ),
                            ),
                            ( "post_data",
                              Tuple(
                                  title = _("Send HTTP POST data"),
                                  elements = [
                                      TextAscii(
                                          title = _("HTTP POST data"),
                                          help = _("Data to send via HTTP POST method. "
                                                   "Please make sure, that the data is URL-encoded."),
                                          size = 40,
                                      ),
                                      TextAscii(
                                          title = _("Content-Type"),
                                          default_value = "text/html"),
                                 ])
                            ),
                            ( "method",
                              DropdownChoice(
                                  title = _("HTTP Method"),
                                  default_value = "GET",
                                  choices = [
                                    ( "GET", "GET" ),
                                    ( "POST", "POST" ),
                                    ( "OPTIONS", "OPTIONS" ),
                                    ( "TRACE", "TRACE" ),
                                    ( "PUT", "PUT" ),
                                    ( "DELETE", "DELETE" ),
                                    ( "HEAD", "HEAD" ),
                                    ( "CONNECT", "CONNECT" ),
                                  ])
                            ),
                            ( "no_body",
                              FixedValue(
                                  value = True,
                                  title = _("Don't wait for document body"),
                                  help = _("Note: this still does an HTTP GET or POST, not a HEAD."),
                                  totext = _("dont wait for body"))
                            ),
                            ( "page_size",
                              Tuple(
                                  title = _("Page size to expect"),
                                  elements = [
                                      Integer(title = _("Minimum"), unit=_("Bytes")),
                                      Integer(title = _("Maximum"), unit=_("Bytes")),
                                  ])
                            ),
                            ( "max_age",
                              Age(
                                  title = _("Maximum age"),
                                  help = _("Warn, if the age of the page is older than this"),
                                  default_value = 3600 * 24,
                              )
                            ),
                            ( "urlize",
                              FixedValue(
                                  value = True,
                                  title = _("Clickable URLs"),
                                  totext = _("Format check output as hyperlink"),
                                  help = _("With this option the check produces an output that is a valid hyperlink "
                                           "to the checked URL and this clickable."),
                              )
                            ),
                        ]
                    ),

                    Dictionary(
                        title = _("Check SSL Certificate Age"),
                        elements = [
                            ( "cert_days",
                               Integer(
                                   title = _("Age"),
                                   help = _("Minimum number of days a certificate has to be valid. "
                                            "Port defaults to 443. When this option is used the URL "
                                            "is not checked."),
                                   unit = _("days"),
                               )
                            ),
                            ( "cert_host",
                                TextAscii(
                                    title = _("Check Cerficate on diffrent IP/ DNS Name"),
                                    help = _("For each SSL cerficate on a host, a diffrent IP address is needed. "
                                             "Here you can specify there address if it differs from the  "
                                             "address from the host primary address."),
                                )
                            ),
                            ("port",
                                Integer(
                                    title = _("TCP Port"),
                                    minvalue = 1,
                                    maxvalue = 65535,
                                    default_value = 443,
                                )
                            ),
                            ( "sni",
                              FixedValue(
                                  value = True,
                                  totext = _("enable SNI"),
                                  title = _("Enable SSL/TLS hostname extension support (SNI)"),
                              )
                            ),
                        ],
                        required_keys = [ "cert_days" ],
                    ),
                ]
            ),
        ]
    ),
    match = 'all')

register_rule(group,
    "active_checks:ldap",
    Tuple(
        title = _("Check access to LDAP service"),
        help = _("This check uses <tt>check_ldap</tt> from the standard "
                "Nagios plugins in order to try the response of an LDAP "
                "server."),
        elements = [
            TextUnicode(
                title = _("Name"),
                help = _("The service description will be <b>LDAP</b> plus this name"),
                allow_empty = False),
            TextAscii(
                title = _("Base DN"),
                help = _("LDAP base, e.g. ou=Development, o=Mathias Kettner GmbH, c=de"),
                allow_empty = False,
                size = 60),
            Dictionary(
               title = _("Optional parameters"),
               elements = [
                   ( "attribute",
                     TextAscii(
                         title = _("Attribute to search"),
                         help = _("LDAP attribute to search, "
                                  "The default is <tt>(objectclass=*)</tt>."),
                         size = 40,
                         allow_empty = False,
                         default_value = "(objectclass=*)",
                     )
                   ),
                   ( "authentication",
                     Tuple(
                         title = _("Authentication"),
                         elements = [
                             TextAscii(
                                 title = _("Bind DN"),
                                 help = _("Distinguished name for binding"),
                                 allow_empty = False,
                                 size = 60,
                             ),
                             TextAscii(
                                 title = _("Password"),
                                 help = _("Password for binding, if you server requires an authentication"),
                                 allow_empty = False,
                                 size = 20,
                             )
                        ]
                      )
                   ),
                   ( "port",
                     Integer(
                       title = _("TCP Port"),
                       help = _("Default is 389 for normal connetions and 636 for SSL connections."),
                       minvalue = 1,
                       maxvalue = 65535,
                       default_value = 389)
                   ),
                   ( "ssl",
                      FixedValue(
                          value = True,
                          totext = _("Use SSL"),
                          title = _("Use LDAPS (SSL)"),
                          help = _("Use LDAPS (LDAP SSLv2 method). This sets the default port number to 636"))

                   ),
                   ( "version",
                     DropdownChoice(
                        title = _("LDAP Version"),
                        help = _("The default is to use version 2"),
                        choices = [
                            ( "v2", _("Version 2") ),
                            ( "v3", _("Version 3") ),
                            ( "v3tls", _("Version 3 and TLS") ),
                        ],
                        default_value = "v2",
                      )
                   ),
                   ( "response_time",
                     Tuple(
                         title = _("Expected response time"),
                         elements = [
                             Float(
                                 title = _("Warning if above"),
                                 unit = "ms",
                                 default_value = 1000.0),
                             Float(
                                 title = _("Critical if above"),
                                 unit = "ms",
                                 default_value = 2000.0),
                         ])
                    ),
                    ( "timeout",
                      Integer(
                          title = _("Seconds before connection times out"),
                          unit = _("sec"),
                          default_value = 10,
                      )
                    ),
                ])
        ]),
    match = 'all'
)

register_rule(group,
    "active_checks:smtp",
    Tuple(
        title = _("Check access to SMTP services"),
        help = _("This check uses <tt>check_smtp</tt> from the standard "
                "Nagios plugins in order to try the response of an SMTP "
                "server."),
        elements = [
            TextUnicode(
                title = _("Name"),
                help = _("The service description will be <b>SMTP</b> plus this name"),
                allow_empty = False),
            Dictionary(
               title = _("Optional parameters"),
               elements = [
                   ( "hostname",
                     TextAscii(
                         title = _("DNS Hostname or IP address"),
                         allow_empty = False,
                         help = _("You can specify a hostname or IP address different from IP address "
                                  "of the host as configured in your host properties."))),
                   ( "port",
                     TextAscii(
                         title = _("TCP Port to connect to"),
                         help = _("The TCP Port the SMTP server is listening on. "
                                  "The default is <tt>25</tt>."),
                         size = 5,
                         allow_empty = False,
                         default_value = "25",
                     )
                   ),
                   ( "ip_version",
                     Alternative(
                         title = _("IP-Version"),
                         elements = [
                            FixedValue(
                                "ipv4",
                                totext = "",
                                title = _("IPv4")
                            ),
                            FixedValue(
                                "ipv6",
                                totext = "",
                                title = _("IPv6")
                            ),
                         ],
                     ),
                   ),
                   ( "expect",
                     TextAscii(
                         title = _("Expected String"),
                         help = _("String to expect in first line of server response. "
                                  "The default is <tt>220</tt>."),
                         size = 8,
                         allow_empty = False,
                         default_value = "220",
                     )
                   ),
                   ('commands',
                     ListOfStrings(
                         title = _("SMTP Commands"),
                         help = _("SMTP commands to execute."),
                     )
                   ),
                   ('command_responses',
                     ListOfStrings(
                         title = _("SMTP Responses"),
                         help = _("Expected responses to the given SMTP commands."),
                     )
                   ),
                   ("from",
                     TextAscii(
                         title = _("FROM-Address"),
                         help = _("FROM-address to include in MAIL command, required by Exchange 2000"),
                         size = 20,
                         allow_empty = True,
                         default_value = "",
                     )
                   ),
                   ("fqdn",
                     TextAscii(
                         title = _("FQDN"),
                         help = _("FQDN used for HELO"),
                         size = 20,
                         allow_empty = True,
                         default_value = "",
                     )
                   ),
                   ("cert_days",
                      Integer(
                          title = _("Minimum Certificate Age"),
                          help = _("Minimum number of days a certificate has to be valid."),
                          unit = _("days"),
                      )
                   ),
                   ("starttls",
                      FixedValue(
                          True,
                          totext = _("STARTTLS enabled."),
                          title = _("Use STARTTLS for the connection.")
                      )
                   ),
                   ( "auth",
                     Tuple(
                         title = _("Enable SMTP AUTH (LOGIN)"),
                         help = _("SMTP AUTH type to check (default none, only LOGIN supported)"),
                         elements = [
                             TextAscii(
                                 title = _("Username"),
                                 size = 12,
                                 allow_empty = False),
                             TextAscii(
                                 title = _("Password"),
                                 size = 12,
                                 allow_empty = False),
                         ]
                     )
                   ),
                   ("response_time",
                     Tuple(
                         title = _("Expected response time"),
                         elements = [
                             Integer(
                                 title = _("Warning if above"),
                                 unit = "sec"
                             ),
                             Integer(
                                 title = _("Critical if above"),
                                 unit = "sec"
                             ),
                         ])
                    ),
                    ( "timeout",
                      Integer(
                          title = _("Seconds before connection times out"),
                          unit = _("sec"),
                          default_value = 10,
                      )
                    ),
                ])
        ]),
    match = 'all'
)

register_rule(group,
    "active_checks:disk_smb",
    Dictionary(
        title = _("Check access to SMB share"),
        help = _("This ruleset helps you to configure the classical Nagios "
                 "plugin <tt>check_disk_smb</tt> that checks the access to "
                 "filesystem shares that are exported via SMB/CIFS."),
        elements = [
            ( "share",
              TextUnicode(
                  title = _("SMB share to check"),
                  size = 32,
                  allow_empty = False,
            )),
            ( "workgroup",
              TextUnicode(
                  title = _("Workgroup"),
                  help = _("Workgroup or domain used (defaults to <tt>WORKGROUP</tt>)"),
                  size = 32,
                  allow_empty = False,
            )),
            ( "host",
              TextAscii(
                  title = _("NetBIOS name of the server"),
                  help = _("If omitted then the IP address is being used."),
                  size = 32,
                  allow_empty = False,
            )),
            ( "port",
              Integer(
                  title = _("TCP Port"),
                  help = _("TCP port number to connect to. Usually either 139 or 445."),
                  default_value = 445,
                  minvalue = 1,
                  maxvalue = 65535,
            )),
            ( "levels",
              Tuple(
                  title = _("Levels for used disk space"),
                  elements = [
                      Percentage(title = _("Warning if above"), default_value = 85,  allow_int = True),
                      Percentage(title = _("Critical if above"), default_value = 95, allow_int = True),
                  ]
            )),
            ( "auth",
              Tuple(
                  title = _("Authorization"),
                  elements = [
                      TextAscii(
                          title = _("Username"),
                          allow_empty = False,
                          size = 24),
                      Password(
                          title = _("Password"),
                          allow_empty = False,
                          size = 12),
                  ],
            )),
        ],
        required_keys = [ "share", "levels" ],
    ),
    match = 'all')

def PluginCommandLine(addhelp = ""):
    return TextAscii(
          title = _("Command line"),
          help = _("Please enter the complete shell command including "
                   "path name and arguments to execute. You can use Nagios "
                   "macros here. The most important are:<ul>"
                   "<li><tt>$HOSTADDRESS$</tt>: The IP address of the host</li>"
                   "<li><tt>$HOSTNAME$</tt>: The name of the host</li>"
                   "<li><tt>$USER1$</tt>: user macro 1 (usually path to shipped plugins)</li>"
                   "<li><tt>$USER2$</tt>: user marco 2 (usually path to your own plugins)</li>"
                   "</ul>"
                   "If you are using OMD, then you can omit the path and just specify "
                   "the command (e.g. <tt>check_foobar</tt>). This command will be "
                   "searched first in the local plugins directory "
                   "(<tt>~/local/lib/nagios/plugins</tt>) and then in the shipped plugins "
                   "directory (<tt>~/lib/nagios/plugins</tt>) within your site directory."),
          size = "max",
       )

register_rule(group,
    "custom_checks",
    Dictionary(
        title = _("Classical active and passive Nagios checks"),
        help = _("With this ruleset you can configure &quot;classical Nagios checks&quot; "
                 "to be executed directly on your monitoring server. These checks "
                 "will not use Check_MK. It is also possible to configure passive "
                 "checks that are fed with data from external sources via the Nagios "
                 "command pipe."),
        elements = [
            ( "service_description",
              TextUnicode(
                  title = _("Service description"),
                  help = _("Please make sure that this is unique per host "
                         "and does not collide with other services."),
                  allow_empty = False,
                  default_value = _("Customcheck"))
            ),
            ( "command_line",
              PluginCommandLine(addhelp = _("<br><br>"
                   "<b>Passive checks</b>: Do no specify a command line if you want "
                   "to define passive checks.")),
            ),
            ( "command_name",
              TextAscii(
                  title = _("Internal command name"),
                  help = _("If you want, then you can specify a name that will be used "
                           "in the <tt>define command</tt> section for these checks. This "
                           "allows you to a assign a customer PNP template for the performance "
                           "data of the checks. If you omit this, then <tt>check-mk-custom</tt> "
                           "will be used."),
                  size = 32)
            ),
            ( "has_perfdata",
              FixedValue(
                  title = _("Performance data"),
                  value = True,
                  totext = _("process performance data"),
              )
            ),
            ( "freshness",
              Dictionary(
                  title = _("Check freshness"),
                  help = _("Freshness checking is only useful for passive checks when the staleness feature "
                           "is not enough for you. It changes the state of a check to a configurable other state "
                           "when the check results are not arriving in time. Staleness will still grey out the "
                           "test after the corrsponding interval. If you dont want that, you might want to adjust "
                           "the staleness interval as well. The staleness interval is calculated from the normal "
                           "check interval multiplied by the staleness value in the <tt>Global Settings</tt>. "
                           "The normal check interval can be configured in a separate rule for your check."),
                  optional_keys = False,
                  elements = [
                      ( "interval",
                        Integer(
                            title = _("Expected update interval"),
                            label = _("Updates are expected at least every"),
                            unit = _("minutes"),
                            minvalue = 1,
                            default_value = 10,
                      )),
                      ( "state",
                        DropdownChoice(
                            title = _("State in case of absent updates"),
                            choices =  [
                               ( 1, _("WARN") ),
                               ( 2, _("CRIT") ),
                               ( 3, _("UNKNOWN") ),
                            ],
                            default_value = 3,
                      )),
                      ( "output",
                        TextUnicode(
                            title = _("Plugin output in case of absent abdates"),
                            size = 40,
                            allow_empty = False,
                            default_value = _("Check result did not arrive in time")
                      )),
                  ],
               )
            ),

        ],
        required_keys = [ "service_description" ],
    ),
    match = 'all'
)

register_rule(group,
    "active_checks:form_submit",
    Tuple(
        title = _("Check HTML Form Submit"),
        help = _("Check submission of HTML forms via HTTP/HTTPS using the plugin <tt>check_form_submit</tt> "
                 "provided with Check_MK. This plugin provides more functionality as <tt>check_http</tt>, "
                 "as it automatically follows HTTP redirect, accepts and uses cookies, parses forms "
                 "from the requested pages, changes vars and submits them to check the response "
                 "afterwards."),
        elements = [
            TextUnicode(
                title = _("Name"),
                help = _("The name will be used in the service description"),
                allow_empty = False
            ),
            Dictionary(
                title = _("Check the URL"),
                elements = [
                    ("hosts", ListOfStrings(
                        title = _('Check specific host(s)'),
                        help = _('By default, if you do not specify any host addresses here, '
                                 'the host address of the host this service is assigned to will '
                                 'be used. But by specifying one or several host addresses here, '
                                 'it is possible to let the check monitor one or multiple hosts.')
                    )),
                    ("virthost", TextAscii(
                        title = _("Virtual host"),
                        help = _("Set this in order to specify the name of the "
                         "virtual host for the query (using HTTP/1.1). When you "
                         "leave this empty, then the IP address of the host "
                         "will be used instead."),
                        allow_empty = False,
                    )),
                    ("uri", TextAscii(
                        title = _("URI to fetch (default is <tt>/</tt>)"),
                        allow_empty = False,
                        default_value = "/",
                        regex = '^/.*',
                    )),
                    ("port", Integer(
                        title = _("TCP Port"),
                        minvalue = 1,
                        maxvalue = 65535,
                        default_value = 80,
                    )),
                    ("ssl", FixedValue(
                        value = True,
                        totext = _("use SSL/HTTPS"),
                        title = _("Use SSL/HTTPS for the connection."))
                    ),
                    ("timeout", Integer(
                        title = _("Seconds before connection times out"),
                        unit = _("sec"),
                        default_value = 10,
                    )),
                    ("expect_regex", RegExp(
                        title = _("Regular expression to expect in content"),
                    )),
                    ("form_name", TextAscii(
                        title = _("Name of the form to populate and submit"),
                        help = _("If there is only one form element on the requested page, you "
                                 "do not need to provide the name of that form here. But if you "
                                 "have several forms on that page, you need to provide the name "
                                 "of the form here, to make the check able to identify the correct "
                                 "form element."),
                        allow_empty = True,
                    )),
                    ("query", TextAscii(
                        title = _("Send HTTP POST data"),
                        help = _("Data to send via HTTP POST method. Please make sure, that the data "
                                 "is URL-encoded (for example \"key1=val1&key2=val2\")."),
                        size = 40,
                    )),
                    ("num_succeeded", Tuple(
                        title = _("Multiple Hosts: Number of successful results"),
                        elements = [
                            Integer(title = _("Warning if equal or below")),
                            Integer(title = _("Critical if equal or below")),
                        ]
                    )),
                ]
            ),
        ]
    ),
    match = 'all'
)
