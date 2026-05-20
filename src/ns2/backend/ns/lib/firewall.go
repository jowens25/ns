package lib

type FirewallInfo struct {
	Enable bool   `json:"Enable" binding:"required"`
	Status string `json:"Status" binding:"required"`

	//Status string `json:"Status" binding:"required"`
	//Status string `json:"Status" binding:"required"`
	//Status string `json:"Status" binding:"required"`

}

func GetFirewallInfo() (FirewallInfo, error) {
	var err error = nil

	fw := FirewallInfo{}

	fw.Status, err = _getUnitStatus("firewalld.service")

	fw.Status = "TEST"

	if err != nil {
		return fw, err
	}

	return fw, nil

}
