#!/usr/bin/perl

use strict;
use warnings;
use XML::Simple;
use LWP::Simple;
use Data::Dumper;

# Turn off output buffering
$|=1;

my $e164map = 0;

sub main
{
	if ( $ARGV[0] =~ /^$/ || $ARGV[1] =~ /^$/ ) {
		print "\nERROR: Missing parameters\n";
		print "usage: npalookup.pl [NPA] [NXX]\n";
		exit(1);
	}

	if ( $ARGV[2] =~ /^e164$/ ) {
		$e164map = 1;
	}

	print "Looking up NPA $ARGV[0] NXX $ARGV[1]\n";
	print "Downloading...\n";

	# Download local area codes and dial plan from localcallingguide.com
	my $localprefixes = get("http://localcallingguide.com/xmllocalprefix.php?npa=$ARGV[0]&nxx=$ARGV[1]");
	my $dialplan = get("http://localcallingguide.com/xmldialplan.php?npa=$ARGV[0]");

	my $parser = new XML::Simple;

	print ("Parsing...\n");
	my $dom = $parser->XMLin( $localprefixes );
	#print Dumper( $dom );
	my @entries = @{ $dom->{'lca-data'}->{'prefix'} };
	my %npas;

	print "\nLocal NPAs:\n";

	foreach my $npa ( @entries ) {
		push( @{ $npas{ $npa->{'npa'} } }, $npa->{'nxx'} );
		#$npas{ $npa->{'npa'} } = 1;
	}

	foreach my $npa ( keys %npas ) {
		print "  $npa\n";
	}

	print "\n";

	$dom = $parser->XMLin( $dialplan );

	# I keep finding odd spaces in these fields.
	foreach my $key ( keys $dom->{'dpdata'} ) {
		$dom->{'dpdata'}->{ $key } =~ s/\s//g;
	}

	#print Dumper( $dom );

	print "Dial Plan:\n";
	print "  Local (HNPA): " . $dom->{'dpdata'}->{'std_hnpa_local'} . "\n";
	print "  Local (FNPA): " . $dom->{'dpdata'}->{'std_fnpa_local'} . "\n";
	print "   Toll (HNPA): " . $dom->{'dpdata'}->{'std_hnpa_toll'} . "\n";
	print "   Toll (FNPA): " . $dom->{'dpdata'}->{'std_fnpa_toll'} . "\n";
	print "   Oper Assist: " . $dom->{'dpdata'}->{'std_oper_assis'} . "\n";
	print "\n";

	if ( $e164map ) {
		print "e164-maps:\n";
		foreach my $npa ( sort keys %npas ) {
			foreach my $nxx ( @{ $npas{ $npa } } ) {
				print " e164 \+1$npa$nxx....\n";
			}
		}
	}
}

main();
