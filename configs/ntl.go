package lib

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
)

const ConfSlaveCoreType int = 1
const ClkClockCoreType int = 2
const ClkSignalGeneratorCoreType int = 3
const ClkSignalTimestamperCoreType int = 4
const IrigSlaveCoreType int = 5
const IrigMasterCoreType int = 6
const PpsSlaveCoreType int = 7
const PpsMasterCoreType int = 8
const PtpOrdinaryClockCoreType int = 9
const PtpTransparentClockCoreType int = 10
const PtpHybridClockCoreType int = 11
const RedHsrPrpCoreType int = 12
const RtcSlaveCoreType int = 13
const RtcMasterCoreType int = 14
const TodSlaveCoreType int = 15
const TodMasterCoreType int = 16
const TapSlaveCoreType int = 17
const DcfSlaveCoreType int = 18
const DcfMasterCoreType int = 19
const RedTsnCoreType int = 20
const TsnIicCoreType int = 21
const NtpServerCoreType int = 22
const NtpClientCoreType int = 23
const ClkFrequencyGeneratorCoreType int = 25
const SynceNodeCoreType int = 26
const PpsClkToPpsCoreType int = 27
const PtpServerCoreType int = 28
const PtpClientCoreType int = 29

var ClkClockProperties = map[string]int{
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

var ClkPropsOrdered = []string{
	"version",
	"status",
	"seconds",
	"nanoseconds",
	"insync",
	"inholdover",
	"insyncthreshold",
	"source",
	"drift",
	"driftinterval",
	"offset",
	"offsetinterval",
	"correctedoffset",
	"correcteddrift",
	"date",
}

var NtpServerProperties = map[string]int{

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

var NtpPropsOrdered = []string{

	"version",
	"status",
	"ipmode",
	"ipaddress",
	"macaddress",
	"vlanstatus",
	"vlanaddress",
	"unicastmode",
	"multicastmode",
	"broadcastmode",
	"precisionvalue",
	"pollintervalvalue",
	"stratumvalue",
	"referenceid",
	"smearingstatus",
	"leap61inprogress",
	"leap59inprogress",
	"leap61status",
	"leap59status",
	"utcoffsetstatus",
	"utcoffsetvalue",
	"requestsvalue",
	"responsesvalue",
	"requestsdroppedvalue",
	"broadcastsvalue",
	"clearcountersstatus",
}

//type NtpServer struct {
//	version              string `json:"version"`
//	status               string `json:"status"`
//	ipmode               string `json:"ipmode"`
//	ipaddress            string `json:"ipaddress"`
//	macaddress           string `json:"macaddress"`
//	vlanstatus           string `json:"vlanstatus"`
//	vlanaddress          string `json:"vlanaddress"`
//	unicastmode          string `json:"unicastmode"`
//	multicastmode        string `json:"multicastmode"`
//	broadcastmode        string `json:"broadcastmode"`
//	precisionvalue       string `json:"precisionvalue"`
//	pollintervalvalue    string `json:"pollintervalvalue"`
//	stratumvalue         string `json:"stratumvalue"`
//	referenceid          string `json:"referenceid"`
//	smearingstatus       string `json:"smearingstatus"`
//	leap61inprogress     string `json:"leap61inprogress"`
//	leap59inprogress     string `json:"leap59inprogress"`
//	leap61status         string `json:"leap61status"`
//	leap59status         string `json:"leap59status"`
//	utcoffsetstatus      string `json:"utcoffsetstatus"`
//	utcoffsetvalue       string `json:"utcoffsetvalue"`
//	requestsvalue        string `json:"requestsvalue"`
//	responsesvalue       string `json:"responsesvalue"`
//	requestsdroppedvalue string `json:"requestsdroppedvalue"`
//	broadcastsvalue      string `json:"broadcastsvalue"`
//	clearcountersstatus  string `json:"clearcountersstatus"`
//}

var PpsSlaveProperties = map[string]int{
	"version":         0,
	"enablestatus":    1,
	"polarity":        2,
	"inputokstatus":   3,
	"pulsewidthvalue": 4,
	"cabledelayvalue": 5,
}

var PpsPropsOrdered = []string{
	"version",
	"enablestatus",
	"polarity",
	"inputokstatus",
	"pulsewidthvalue",
	"cabledelayvalue",
}

var PtpOcProperties = map[string]int{
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

var PtpPropsOrdered = []string{
	"version",
	"vlanaddress",
	"vlanstatus",
	"profile",
	"layer",
	"delaymechanismvalue",
	"ipaddress",
	"status",
	"defaultdsclockid",
	"defaultdsdomain",
	"defaultdspriority1",
	"defaultdspriority2",
	"defaultdsaccuracy",
	"defaultdsclass",
	"defaultdsvariance",
	"defaultdsshortid",
	"defaultdsinaccuracy",
	"defaultdsnumberofports",
	"defaultdstwostepstatus",
	"defaultdssignalingstatus",
	"defaultdsmasteronlystatus",
	"defaultdsslaveonlystatus",
	"defaultdslistedunicastslavesonlystatus",
	"defaultdsdisableoffsetcorrectionstatus",
	"portdspeerdelayvalue",
	"portdsstate",
	"portdsasymmetryvalue",
	"portdsmaxpeerdelayvalue",
	"portdspdelayreqlogmsgintervalvalue",
	"portdsdelayreqlogmsgintervalvalue",
	"portdsdelayreceipttimeoutvalue",
	"portdsannouncelogmsgintervalvalue",
	"portdsannouncereceipttimeoutvalue",
	"portdssynclogmsgintervalvalue",
	"portdssyncreceipttimeoutvalue",
	"currentdsstepsremovedvalue",
	"currentdsoffsetvalue",
	"currentdsdelayvalue",
	"parentdsparentclockidvalue",
	"parentdsgmclockidvalue",
	"parentdsgmpriority1value",
	"parentdsgmpriority2value",
	"parentdsgmvariancevalue",
	"parentdsgmaccuracyvalue",
	"parentdsgmclassvalue",
	"parentdsgmshortidvalue",
	"parentdsgminaccuracyvalue",
	"parentdsnwinaccuracyvalue",
	"timepropertiesdstimesourcevalue",
	"timepropertiesdsptptimescalestatus",
	"timepropertiesdsfreqtraceablestatus",
	"timepropertiesdstimetraceablestatus",
	"timepropertiesdsleap61status",
	"timepropertiesdsleap59status",
	"timepropertiesdsutcoffsetvalstatus",
	"timepropertiesdsutcoffsetvalue",
	"timepropertiesdscurrentoffsetvalue",
	"timepropertiesdsjumpsecondsvalue",
	"timepropertiesdsnextjumpvalue",
	"timepropertiesdsdisplaynamevalue",
}

var TodSlaveProperties = map[string]int{
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

var TodPropsOrdered = []string{
	"version",
	"protocol",
	"gnss",
	"msgdisable",
	"correction",
	"baudrate",
	"invertedpolarity",
	"utcoffset",
	"utcinfovalid",
	"leapannounce",
	"leap59",
	"leap61",
	"leapinfovalid",
	"timetoleap",
	"gnssfix",
	"gnssfixok",
	"spoofingstate",
	"fixandspoofinginfovalid",
	"jamminglevel",
	"jammingstate",
	"antennastate",
	"antennaandjamminginfovalid",
	"nrofsatellitesseen",
	"nrofsatelliteslocked",
	"nrofsatellitesinfo",
	"enable",
	"inputok",
}

func ReadAllNtp() {

	for _, p := range NtpPropsOrdered {

		rsp, err := ReadNtlProperty("ntp", p)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(rsp[0], rsp[1], rsp[2])
	}

}

func ReadAllClk() {
	for _, p := range ClkPropsOrdered {

		rsp, err := ReadNtlProperty("clk", p)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(rsp[0], rsp[1], rsp[2])
	}
}

func ReadAllPps() {
	for _, p := range PpsPropsOrdered {

		rsp, err := ReadNtlProperty("pps", p)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(rsp[0], rsp[1], rsp[2])
	}
}

func ReadAllPtp() {
	for _, p := range PtpPropsOrdered {

		rsp, err := ReadNtlProperty("ptp", p)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(rsp[0], rsp[1], rsp[2])
	}
}

func ReadAllTod() {
	for _, p := range TodPropsOrdered {

		rsp, err := ReadNtlProperty("tod", p)

		if err != nil {
			fmt.Println(err.Error())
		}
		fmt.Println(rsp[0], rsp[1], rsp[2])
	}
}

func readNtlPropertyHandler(c *gin.Context) {

	//fmt.Println("TESTING")

	module := c.Param("module")
	property := c.Param("property")
	//fmt.Println("TESTING")

	info, err := ReadNtlProperty(module, property)
	if err != nil {
		fmt.Println("ntl operate error in ntp read")
		fmt.Println(err.Error())

		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	fmt.Println("TESTING")

	c.JSON(http.StatusOK, gin.H{property: info[2]})
}

func ReadNtlProperty(module string, property string) ([3]string, error) {

	var moduleProperties map[string]int
	var moduleType int
	ret := [3]string{"", "", ""}

	switch module {

	case "clk":
		moduleType = ClkClockCoreType
		moduleProperties = ClkClockProperties
	case "ntp":
		moduleType = NtpServerCoreType
		moduleProperties = NtpServerProperties
	case "pps":
		moduleType = PpsSlaveCoreType
		moduleProperties = PpsSlaveProperties
	case "ptp":
		moduleType = PtpOrdinaryClockCoreType
		moduleProperties = PtpOcProperties
	case "tod":
		moduleType = TodSlaveCoreType
		moduleProperties = TodSlaveProperties

	default:
		return ret, fmt.Errorf("NO SUCH MODULE")

	}

	// cmd := "$GPNTL,MM,PP,?" -> gets fresh value from fpga
	// cmd := "$GPNTL,MM,PP"   -> gets stored value from 4078
	// TODO: Implement struct reads, read from struct normally. read directly when needed.. live updates

	prop, ok := moduleProperties[property]

	if !ok {
		fmt.Println("prop not found")
		return ret, fmt.Errorf("PROPERTY NOT FOUND")
	}

	cmd := fmt.Sprintf("$GPNTL,%d,%d,?", moduleType, prop)
	response, err := ReadWriteSocket(cmd)

	parts := strings.Split(response, ",")

	value := parts[3]

	if err != nil {
		fmt.Println("axi operate error in ntp read")
		fmt.Println(err.Error())

		return ret, fmt.Errorf("READ WRITE MIRCO ERROR")
	}
	ret = [3]string{module, property, value}
	//return module, property, value
	return ret, nil
}

func writeNtlPropertyHandler(c *gin.Context) {

	module := c.Param("module")
	property := c.Param("property")

	var data map[string]string
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	value := data[property]

	info, err := WriteNtlProperty(module, property, value)

	if err != nil {
		log.Println("axi operate error in ntp read")
		log.Println(err.Error())

		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{property: info[2]})
}

func WriteNtlProperty(module string, property string, value string) ([3]string, error) {

	var moduleProperties map[string]int
	var moduleType int

	ret := [3]string{"", "", ""}

	switch module {

	case "clk":
		moduleType = ClkClockCoreType
		moduleProperties = ClkClockProperties
	case "ntp":
		moduleType = NtpServerCoreType
		moduleProperties = NtpServerProperties
	case "pps":
		moduleType = PpsSlaveCoreType
		moduleProperties = PpsSlaveProperties
	case "ptp":
		moduleType = PtpOrdinaryClockCoreType
		moduleProperties = PtpOcProperties
	case "tod":
		moduleType = TodSlaveCoreType
		moduleProperties = TodSlaveProperties

	default:

		return ret, fmt.Errorf("NO SUCH MODULE")

	}

	prop, ok := moduleProperties[property]

	if !ok {
		return ret, fmt.Errorf("PROPERTY NOT FOUND")
	}

	cmd := fmt.Sprintf("$GPNTL,%d,%d,%s", moduleType, prop, value)
	response, err := ReadWriteSocket(cmd)
	if err != nil {
		log.Println("axi operate error in ntl write")
		log.Println(err.Error())

		return ret, fmt.Errorf("READ MCU ERROR")
	}
	parts := strings.Split(response, ",")

	value = parts[3]

	ret = [3]string{module, property, value}

	return ret, nil

}

func LoadConfig(fileName string) {

	fmt.Println("LOADING CONFIG...")

	data, err := os.ReadFile(fileName)
	if err != nil {
		log.Println("file err: ", err)
	}

	for _, line := range strings.Split(string(data), "\n") {
		//fmt.Println(line)

		if strings.Contains(line, "--") {
			// a comment
			continue

		} else if strings.Contains(line, "$WC") {

			line = strings.Trim(line, "\r\n")

			rsp, err := ReadWriteSocket(line)

			if strings.HasPrefix(rsp, "$ER") {
				fmt.Println("config load err")
				return
			}

			if err != nil {
				fmt.Println("config error")
				return
			}

			fmt.Println(rsp)

		}

	}

}

func ppsHandler(c *gin.Context) {

	rsp, err := ReadSocket("$GPNVS,10")
	if err != nil {
		fmt.Println("socket error")
	}

	r := strings.Split(rsp, ",")

	c.JSON(http.StatusOK, gin.H{
		"pps": r[6],
	})
}
