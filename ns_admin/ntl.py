
CONFSLAVECORETYPE = 1
CLKCLOCKCORETYPE = 2
CLKSIGNALGENERATORCORETYPE = 3
CLKSIGNALTIMESTAMPERCORETYPE = 4
IRIGSLAVECORETYPE = 5
IRIGMASTERCORETYPE = 6
PPSSLAVECORETYPE = 7
PPSMASTERCORETYPE = 8
PTPORDINARYCLOCKCORETYPE = 9
PTPTRANSPARENTCLOCKCORETYPE = 10
PTPHYBRIDCLOCKCORETYPE = 11
REDHSRPRPCORETYPE = 12
RTCSLAVECORETYPE = 13
RTCMASTERCORETYPE = 14
TODSLAVECORETYPE = 15
TODMASTERCORETYPE = 16
TAPSLAVECORETYPE = 17
DCFSLAVECORETYPE = 18
DCFMASTERCORETYPE = 19
REDTSNCORETYPE = 20
TSNIICCORETYPE = 21
NTPSERVERCORETYPE = 22
NTPCLIENTCORETYPE = 23
CLKFREQUENCYGENERATORCORETYPE = 25
SYNCENODECORETYPE = 26
PPSCLKTOPPSCORETYPE = 27
PTPSERVERCORETYPE = 28
PTPCLIENTCORETYPE = 29

ClkClockProperties = {
	"version":         0,
	"status":          1,
	"seconds":         2,
	"nanoseconds":     3,
	"insync":          4,
	"inholdover":      5,
	"insyncthreshold": 6,
	"source":          7,
	"drift":           8,
	"driftinterval":   9,
	"offset":          10,
	"offsetinterval":  11,
	"correctedoffset": 12,
	"correcteddrift":  13,
	"date":            14,
}



NtpServerProperties = {

	"version":              0,
	"status":               1,
	"ipmode":               2,
	"ipaddress":            3,
	"macaddress":           4,
	"vlanstatus":           5,
	"vlanaddress":          6,
	"unicastmode":          7,
	"multicastmode":        8,
	"broadcastmode":        9,
	"precisionvalue":       10,
	"pollintervalvalue":    11,
	"stratumvalue":         12,
	"referenceid":          13,
	"smearingstatus":       14,
	"leap61inprogress":     15,
	"leap59inprogress":     16,
	"leap61status":         17,
	"leap59status":         18,
	"utcoffsetstatus":      19,
	"utcoffsetvalue":       20,
	"requestsvalue":        21,
	"responsesvalue":       22,
	"requestsdroppedvalue": 23,
	"broadcastsvalue":      24,
	"clearcountersstatus":  25,
}



PpsSlaveProperties = {
	"version":         0,
	"enablestatus":    1,
	"polarity":        2,
	"inputokstatus":   3,
	"pulsewidthvalue": 4,
	"cabledelayvalue": 5,
}



PtpOcProperties = {
	"version":                                0,
	"vlanaddress":                            1,
	"vlanstatus":                             2,
	"profile":                                3,
	"layer":                                  4,
	"delaymechanismvalue":                    5,
	"ipaddress":                              6,
	"status":                                 7,
	"defaultdsclockid":                       8,
	"defaultdsdomain":                        9,
	"defaultdspriority1":                     10,
	"defaultdspriority2":                     11,
	"defaultdsaccuracy":                      12,
	"defaultdsclass":                         13,
	"defaultdsvariance":                      14,
	"defaultdsshortid":                       15,
	"defaultdsinaccuracy":                    16,
	"defaultdsnumberofports":                 17,
	"defaultdstwostepstatus":                 18,
	"defaultdssignalingstatus":               19,
	"defaultdsmasteronlystatus":              20,
	"defaultdsslaveonlystatus":               21,
	"defaultdslistedunicastslavesonlystatus": 22,
	"defaultdsdisableoffsetcorrectionstatus": 23,
	"portdspeerdelayvalue":                   24,
	"portdsstate":                            25,
	"portdsasymmetryvalue":                   26,
	"portdsmaxpeerdelayvalue":                27,
	"portdspdelayreqlogmsgintervalvalue":     28,
	"portdsdelayreqlogmsgintervalvalue":      29,
	"portdsdelayreceipttimeoutvalue":         30,
	"portdsannouncelogmsgintervalvalue":      31,
	"portdsannouncereceipttimeoutvalue":      32,
	"portdssynclogmsgintervalvalue":          33,
	"portdssyncreceipttimeoutvalue":          34,
	"currentdsstepsremovedvalue":             35,
	"currentdsoffsetvalue":                   36,
	"currentdsdelayvalue":                    37,
	"parentdsparentclockidvalue":             38,
	"parentdsgmclockidvalue":                 39,
	"parentdsgmpriority1value":               40,
	"parentdsgmpriority2value":               41,
	"parentdsgmvariancevalue":                42,
	"parentdsgmaccuracyvalue":                43,
	"parentdsgmclassvalue":                   44,
	"parentdsgmshortidvalue":                 45,
	"parentdsgminaccuracyvalue":              46,
	"parentdsnwinaccuracyvalue":              47,
	"timepropertiesdstimesourcevalue":        48,
	"timepropertiesdsptptimescalestatus":     49,
	"timepropertiesdsfreqtraceablestatus":    50,
	"timepropertiesdstimetraceablestatus":    51,
	"timepropertiesdsleap61status":           52,
	"timepropertiesdsleap59status":           53,
	"timepropertiesdsutcoffsetvalstatus":     54,
	"timepropertiesdsutcoffsetvalue":         55,
	"timepropertiesdscurrentoffsetvalue":     56,
	"timepropertiesdsjumpsecondsvalue":       57,
	"timepropertiesdsnextjumpvalue":          58,
	"timepropertiesdsdisplaynamevalue":       59,
}



TodSlaveProperties = {
	"version":                    0,
	"protocol":                   1,
	"gnss":                       2,
	"msgdisable":                 3,
	"correction":                 4,
	"baudrate":                   5,
	"invertedpolarity":           6,
	"utcoffset":                  7,
	"utcinfovalid":               8,
	"leapannounce":               9,
	"leap59":                     10,
	"leap61":                     11,
	"leapinfovalid":              12,
	"timetoleap":                 13,
	"gnssfix":                    14,
	"gnssfixok":                  15,
	"spoofingstate":              16,
	"fixandspoofinginfovalid":    17,
	"jamminglevel":               18,
	"jammingstate":               19,
	"antennastate":               20,
	"antennaandjamminginfovalid": 21,
	"nrofsatellitesseen":         22,
	"nrofsatelliteslocked":       23,
	"nrofsatellitesinfo":         24,
	"enable":                     25,
	"inputok":                    26,
}

