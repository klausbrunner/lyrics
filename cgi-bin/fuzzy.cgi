#!/usr/bin/perl
# !/usr/local/bin/perl5
# fuzzy search (n-gram similarity) in formatierter liedtext-datenbank
# klaus a. brunner 1998


$dbase =     'lyrics.txt';   # name der datenbank
$template =  'search-template.html'; # vorlage fuer resultat
$log =       'fuzzy.log';            # name des fehler-logfiles

# ----------------------------------------
 # $starttime = (times)[0];		# debug!

# parameter isolieren und vorbereiten
if (&ReadParse(*input)) {
    $srch = $input{'pattern'};
    $maxmatch = $input{'maxmatch'};
} else {
   &req_error ('Internal Error: There are CGI arguments missing (method=get!).');
}

 # $srch = 'rocking in the free world';	# debug!

$search_mode              = 'fuzzy';
$matchlimit               = 35;
$absolute_length_minimum  = 3;
$absolute_length_maximum  = 40;
$fuzzy_mode_threshold     = 5;
$mixed_mode_threshold     = 8;
$maxmatch               ||= 80;


# prepare string
($srch2 = $srch) =~ tr/A-Za-z//cd;

# do some length checks
$srchlen = length($srch2);
if ($srchlen < $absolute_length_minimum) {
    &req_error("Please enter at least one word with $absolute_length_minimum letters.");
} elsif ($srchlen < $mixed_mode_threshold) {
    $search_mode = 'mixed';
    $matchlimit *= 1.35;
    if ($srchlen < $fuzzy_mode_threshold) {
	$search_mode = 'exact';
    }
} else {
    $srch = substr($srch, 0, $absolute_length_maximum);
}


# n-gramme bilden
if ($search_mode ne 'exact') {
    $srch = &prepstr($srch);

    # ngramm-laenge festlegen (wichtig: ng1 ist kuerzeres ngramm!)
    $ng1len = (($srchlen < 7) ? 2 : 3);
    $ng2len = (($srchlen < 7) ? 3 : 5);

    # ngramme bilden, dabei keine ueberschneidung zw. worten zulassen
    $ng1cnt = $srchlen - $ng1len + 1;
    $ng2cnt = $srchlen - $ng2len + 1;
    for ($i=0; $i<$ng1cnt; $i++) {
        $tmp = substr($srch, $i, $ng1len);
        if ((substr($tmp, $ng1len-2, 1) eq ' ') and
            (substr($tmp, 0, 1) ne ' ')) {
            $i += $ng1len-3;
        } else {
            $ng1[++$#ng1] = $tmp;
        }
    }
    for ($i=0; $i<$ng2cnt; $i++) {
        $tmp = substr($srch, $i, $ng2len);
        if ((substr($tmp, $ng2len-2, 1) eq ' ') and
            (substr($tmp, 0, 1) ne ' ')) {
            $i += $ng2len-3;
        } else {
            $ng2[++$#ng2] = $tmp;
        }
    }
}
else {
    ($srch) =~ tr/A-Z/a-z/;
    ($srch) =~ tr/a-z/ /cs;
    $ng1[++$#ng1] = $srch;

    $ng1cnt = 1;
    $ng2cnt = 0;
}



# datenbank oeffnen, abbruch bei fehler
open (DBF, $dbase) or &req_error("Internal Error: Sorry, I can't open $dbase ($!).");

# zeilenweise lesen & matchen
$songhits = 0;
while($input = <DBF>) {
    next if ($input =~ /^[|*@]/o);	# referenzen, kommentare ignorieren

    if ($input =~ /^[#\\]/o) {		# album oder song
        chop $input;
        # checken ob beim letzten song matches
        if ($songhits>0) {

            $key = $songbestr+0.1*$songhits;     # eindeutige schluessel!
            while (exists $results{$key}) { $key += 0.0001; }

            $results{$key} = join '',
              "<li>",
              "<A HREF=\"../lyrics-$albid.html#$songid\">$songname</A> ",
              "(from <A HREF=\"../lyrics-$albid.html\">$albname</A>)<BR>",
              "<B>&#8220;<I>$songbestl</I>&#8221;</B><br><br></li>";
            $songhits = 0;
        }
        if ($input =~ /^#/o) {			# song
            $songid=substr($input, 1, 3);
            $songname=substr($input, 4);
            $songbestr=0;
        } else {				# album
            $albid=substr($input, 1, 2);
            $albname=substr($input, 3);
	}
    } else {					# normale textzeile, also suchen

       $cnt1 = $cnt2 = 0;
       $inpf = &prepstr($input);
       foreach $ngram (@ng1) {
           $cnt1++ if (index($inpf, $ngram) >= 0);
       }
       if ($cnt1 > 0) {                 	# nur wenn kuerzere matches (.opt)
           foreach $ngram (@ng2) {
               $cnt2++ if (index($inpf, $ngram) >= 0);
           }

       }
       $ratio = (100 * ($cnt1+$cnt2) / ($#ng1+$#ng2+2));


       if ($ratio > $matchlimit) {               # treffer pruefen
           $songhits++;
           if(($ratio > $songbestr)) {
               $songbestr=$ratio;
               $songbestl=$input;

	       if($search_mode eq 'mixed') {     # zusaetzlich exakte suche
		   $songbestr *= 1.10 if (index($inpf, $srch) >= 0);
	       }
           }
       }

    }
}
close(DBF);


# falls vorhanden, resultate sortiert (beste zuerst) anzeigen
$matchcount = 0;
$overdrive = 0;
$results = '<ul>';
$results .= "<!-- $0 mode=$search_mode -->\n";
foreach $key (sort {$b <=> $a} (keys %results)) {
    $results .= $results{$key};
 #    $results .= "\n<!-- $matchcount, $key -->\n";   # debug

    $matchcount++;

    # bei sehr guten treffern darf maxmatch auch ueberschritten werden,
    # aber hoechstens maxmatch*2
    if (($matchcount == $maxmatch) and (not $overdrive) and ($key > 95)) {
        $overdrive++;
        $maxmatch *= 2;
    }
    last if ($matchcount == $maxmatch);
}
$results .= '</ul>';

if($matchcount < 1) {
   &reply('<P><FONT FACE="Helvetica,Arial" SIZE=+1><B>Sorry, no line seems to match your query!</B></FONT><BR>');
} else {
   &reply($results);
}

# debug!
# printf STDERR "<!-- fuzzy.cgi exec time: %.2fs -->\n", (times)[0] - $starttime;


# -------------------------- ende des hauptprogramms ------------------------

# sonderzeichen weg, lowercase, in spaces einbetten
# (.opt durch einfaches table-lookup?)
sub prepstr {
    my ($t) = $_[0];
    ($t) =~ tr/A-Z/a-z/;
    ($t) =~ tr/a-z/ /cs;
    ' '.$t.' ';
}

# http- und html-header ausgeben
sub reply {
   my ($msg) = $_[0];

   # write http header
   print "Content-Type: text/html\n";			# html, latin-1
   print "Expires: ", &gmtime1123(time+6000), "\n\n";

   # vorlage ausgeben und fuellen
   open(TEMPLATEF, $template) or
      print("Internal Error: Sorry, I can't open $template ($!)");

   while(<TEMPLATEF>) {
      s/<INSERT_TEXT>/$msg/;
      print;
   }

   close(TEMPLATEF);

}

# error msg & exit
sub req_error {
    &reply ("<P><FONT FACE=\"Helvetica,Arial\" SIZE=+1><B>Oops! $_[0] </B></FONT><BR>");

    # anfrage und resultat aufzeichnen
    open(LOGF, ">>$log") and
       print(LOGF gmtime1123(time()), "/$srch/$_[0]",
                  "/$ENV{'HTTP_USER_AGENT'}/$ENV{'REMOTE_HOST'}\n");
    close LOGF;

    exit;
}

# converts time/date as returned by time() function to RFC1123 format in GMT
# for instance: "Thu, 01 Dec 1994 16:00:00 GMT"
sub gmtime1123 {
   my (@wdays,@months,$sec,$min, $hour,$mday,$mon,$year,$wday,$yday,$isdst);

   @wdays = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat");
   @months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
              "Sep", "Oct", "Nov", "Dec");

   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime($_[0]);

   return sprintf "%s, %02d %s %4d %02d:%02d:%02d GMT", $wdays[$wday],
                  $mday, $months[$mon], $year+1900, $hour, $min, $sec;
   # note: this code *is* y2k-safe!
}


# ReadParse by Steven E. Brenner (modified, GET method only)
sub ReadParse {
  local (*in) = @_ if @_;
  my ($i, $key, $val);

  $in = $ENV{'QUERY_STRING'};

  @in = split(/[&;]/,$in);

  foreach $i (0 .. $#in) {
    # Convert plus's to spaces
    $in[$i] =~ s/\+/ /g;

    # Split into key and value.
    ($key, $val) = split(/=/,$in[$i],2); # splits on the first =.

    # Convert %XX from hex numbers to alphanumeric
    $key =~ s/%(..)/pack("c",hex($1))/ge;
    $val =~ s/%(..)/pack("c",hex($1))/ge;

    # Associate key and value
    $in{$key} .= "\0" if (defined($in{$key})); # \0 is the multiple separator
    $in{$key} .= $val;

  }

  return scalar(@in);
}


#----------- eof fuzzy.pl -------------
