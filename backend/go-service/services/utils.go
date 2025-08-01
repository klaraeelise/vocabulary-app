/*
The ScrapeWord function orchestrates the whole process. Especially ensuring the functionality of the loop.
*/

package services

import "strings"

func parseWordFormMetadata(label string) (number, definiteness, gender, degree, tense string) {
	l := strings.ToLower(label)
	if strings.Contains(l, "entall") {
		number = "singular"
	}
	if strings.Contains(l, "flertall") {
		number = "plural"
	}
	if strings.Contains(l, "ubestemt") {
		definiteness = "indefinite"
	}
	if strings.Contains(l, "bestemt") {
		definiteness = "definite"
	}
	if strings.Contains(l, "hankjønn") {
		gender = "masculine"
	}
	if strings.Contains(l, "hunkjønn") {
		gender = "feminine"
	}
	if strings.Contains(l, "intetkjønn") {
		gender = "neuter"
	}
	if strings.Contains(l, "komparativ") {
		degree = "comparative"
	}
	if strings.Contains(l, "superlativ") {
		degree = "superlative"
	}
	if strings.Contains(l, "presens") {
		tense = "present"
	}
	if strings.Contains(l, "preteritum") {
		tense = "past"
	}
	if strings.Contains(l, "perfektum") {
		tense = "perfect"
	}
	return
}

func buildFullLabel(group, label string) string {
	if label != "" && group != "" {
		return group + " / " + label
	} else if label != "" {
		return label
	} else {
		return group
	}
}
