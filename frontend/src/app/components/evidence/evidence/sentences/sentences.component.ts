import {Component, Input, OnInit} from '@angular/core';
import {Evidence} from "../../../../model/evidence";
import {ModelService} from "../../../../service/model.service";
import {EvidenceDAOService} from "../../../../service/dao/evidence-dao.service";
import {C} from "../../../../service/c";
import {MessagesService} from "../../../../service/utilities/messages.service";
import {ScrollService} from "../../../../service/utilities/scroll.service";
import {FormControl, FormGroup, Validators} from "@angular/forms";
import { SemanticQuery } from 'src/app/model/semanticquery';

@Component({
  selector: 'app-sentences',
  templateUrl: './sentences.component.html',
  styleUrls: ['./sentences.component.css']
})
export class SentencesComponent implements OnInit{

  @Input()
  public evidence?: Evidence;

  constructor(private model: ModelService,
              private evidenceDAO: EvidenceDAOService,
              private messages: MessagesService,
              private scrollService: ScrollService) {
  }

  ngOnInit(): void {
    this.semanticQueries = this.evidence!.semanticQueries!;
    this.sentences = this.evidence!.sentences!;
  }



  semanticQueries: SemanticQuery[] = [];
  sentences: string[] = [];


  findSemantic() {
    let projectId = this.model.getPersistentBean<string>(C.SELECTED_PROJECT_ID)!;
    this.evidenceDAO.getSemanticQueries(projectId, this.evidence!).then(sQ => sQ.forEach(type => this.semanticQueries.push(type))).catch(
      error => this.messages.showErrorMessage("Error: " + error));
    this.scrollService.scrollTo("#generateSentenceForm");
  }

  formGenerate = new FormGroup({
    type: new FormControl<string>('', Validators.required),
    number: new FormControl<number>(1, [Validators.required, Validators.min(1)])
  });

  get typeField() {
    return this.formGenerate.get("type")!;
  }

  get numberFIeld() {
    return this.formGenerate.get("number")!;
  }

  generateSentences() {
    let type = this.typeField.value!;
    let semanticQuery = this.semanticQueries.find(q => q.name === type);
    let number = this.numberFIeld.value!;
    console.log("Generating ", number, " sentences of type ", type);
    let projectId = this.model.getPersistentBean<string>(C.SELECTED_PROJECT_ID)!;
    this.evidenceDAO.generateSentence(projectId, this.evidence!, semanticQuery!, number).then(sentences => {
      sentences.forEach(sentence => this.sentences.push(sentence))
    }).catch(error => this.messages.showErrorMessage(error));
    this.scrollService.scrollTo("#sentences");
  }
}
