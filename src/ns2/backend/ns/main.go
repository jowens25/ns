/*
Copyright © 2026 NAME HERE <EMAIL ADDRESS>
*/
package main

import (
	"github.com/jowens25/ns/ns/cmd"
)

func main() {

	//manPage, err := mcobra.NewManPage(1, cmd.Root())
	//if err != nil {
	//	panic(err)
	//}
	//
	//manPage = manPage.WithSection("Copyright", "(C) 2022 Christian Muehlhaeuser.\n"+
	//	"Released under MIT license.")
	//
	//fmt.Println(manPage.Build(roff.NewDocument()))
	//
	//os.WriteFile("temp.docs", []byte(manPage.Build(roff.NewDocument())), 0644)

	cmd.Execute()

	// out := flag.String("out", "./docs/cli", "output directory")
	// format := flag.String("format", "rest", "markdown|man|rest")
	// front := flag.Bool("frontmatter", false, "prepend simple YAML front matter to markdown")
	// flag.Parse()

	// if err := os.MkdirAll(*out, 0o755); err != nil {
	// 	log.Fatal(err)
	// }

	// root := cmd.Root()
	// root.DisableAutoGenTag = true // stable, reproducible files (no timestamp footer)

	// switch *format {
	// case "markdown":
	// 	if *front {
	// 		prep := func(filename string) string {
	// 			base := filepath.Base(filename)
	// 			name := strings.TrimSuffix(base, filepath.Ext(base))
	// 			title := strings.ReplaceAll(name, "_", " ")
	// 			return fmt.Sprintf("---\ntitle: %q\nslug: %q\ndescription: \"CLI reference for %s\"\n---\n\n", title, name, title)
	// 		}
	// 		link := func(name string) string { return strings.ToLower(name) }
	// 		if err := doc.GenMarkdownTreeCustom(root, *out, prep, link); err != nil {
	// 			log.Fatal(err)
	// 		}
	// 	} else {
	// 		if err := doc.GenMarkdownTree(root, *out); err != nil {
	// 			log.Fatal(err)
	// 		}
	// 	}
	// case "man":
	// 	hdr := &doc.GenManHeader{Title: strings.ToUpper(root.Name()), Section: "1"}
	// 	if err := doc.GenManTree(root, hdr, *out); err != nil {
	// 		log.Fatal(err)
	// 	}
	// case "rest":
	// 	if err := doc.GenReSTTree(root, *out); err != nil {
	// 		log.Fatal(err)
	// 	}
	// default:
	// 	log.Fatalf("unknown format: %s", *format)
	// }

}
