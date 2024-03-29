import { AfterViewChecked, Component, Input } from '@angular/core';
import { Project } from "../../model/project";
import { Evidence } from "../../model/evidence";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { EvidenceDAOService } from "../../service/dao/evidence-dao.service";
import { MessagesService } from "../../service/utilities/messages.service";
import { HighlighterService } from "../../service/utilities/highlighter.service";

@Component({
  selector: 'app-evidence',
  templateUrl: './evidence.component.html',
  styleUrls: ['./evidence.component.css']
})
export class EvidenceComponent implements AfterViewChecked {

  constructor(private evidenceDAO: EvidenceDAOService,
    private messages: MessagesService,
    private hightlighter: HighlighterService) {
  }

  @Input()
  public project!: Project;

  ngAfterViewChecked() {
  }

  get evidence(): Evidence[] {
    return this.project.evidence;
  }

  generateEvidenceForm = new FormGroup({
    positiveNumber: new FormControl<number | undefined>(undefined,
      [Validators.required, Validators.min(0)]),
    negativeNumber: new FormControl<number | undefined>(undefined,
      [Validators.required, Validators.min(0)])
  });

  get positiveNumber() {
    return this.generateEvidenceForm.get("positiveNumber")!;
  }

  get negativeNumber() {
    return this.generateEvidenceForm.get("negativeNumber")!;
  }

  generate() {
    let positiveNumber = this.positiveNumber.value!;
    let negativeNumber = this.negativeNumber.value!;
    console.log("Generating evidence: ", positiveNumber, " positive, ", negativeNumber, " negative");
    this.evidenceDAO.generateEvidences(this.project.id!, positiveNumber, negativeNumber).then(generatedEvidence => {
      this.messages.showInfoMessage(`${generatedEvidence.length} evidence generated`);
      generatedEvidence.forEach(e => this.project.evidence.push(e));
    }).catch(error => {
      console.log(error);
      this.messages.showErrorMessage(error);
    });
  }

  private splitQuery(query: string): string {
    let sQuery = query;
    const lineLength = 40;
    const keywords = ["FROM", "WHERE", "GROUP BY"];
    for (let key of keywords) {
      sQuery = sQuery.replace(key, "\n" + key);
    }
    return sQuery.split('\n')
      .map(line => {
        if (line.length > lineLength) {
          const words = line.split(' ');
          let formattedLine = '';
          let currentLength = 0;

          words.forEach(word => {
            if (currentLength + word.length > lineLength) {
              formattedLine += '\n' + word;
              currentLength = word.length;
            } else {
              if (formattedLine !== '') {
                formattedLine += ' ' + word;
                currentLength += word.length + 1;
              } else {
                formattedLine += word;
                currentLength += word.length;
              }
            }
          });
          return formattedLine;
        }
        return line;
      })
      .join('\n');
    return sQuery;
  }

  loadQuery() {
    this.evidenceDAO.getQuery(this.project.id!).then(query => {
      if (query.sql.startsWith('"')) {
        query.sql = query.sql.substring(1, query.sql.length);
      }
      let sql = this.splitQuery(query.sql);
      document.querySelector("#sql")!.innerHTML = sql;
      this.hightlighter.highlightAll();
    }).catch(error => {
      this.messages.showErrorMessage("Error while fetching the query" + error);
    });
  }
}
