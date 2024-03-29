import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ProjectComponent } from './project.component';
import { ProjectRoutingModule } from './project-routing.module';
import { DynamicTableComponent } from 'src/app/components/dynamic-table/dynamic-table.component';
import { LoginComponent } from '../login/login.component';
import { NewProjectComponent } from '../new-project/new-project.component';
import { EvidenceComponent } from 'src/app/components/evidence/evidence.component';
import { SingleEvidenceComponent } from 'src/app/components/evidence/evidence/single-evidence.component';
import { SentencesComponent } from 'src/app/components/evidence/evidence/sentences/sentences.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MtxGridModule } from '@ng-matero/extensions/grid';
import { ExportComponent } from "../../components/export/export.component";
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { ExportDialogComponent } from 'src/app/components/export-dialog/export-dialog.component';


@NgModule({
    declarations: [
        ProjectComponent,
        DynamicTableComponent,
        LoginComponent,
        NewProjectComponent,
        EvidenceComponent,
        SingleEvidenceComponent,
        SentencesComponent,
        ExportComponent,
        ExportDialogComponent
    ],
    imports: [
        CommonModule,
        ProjectRoutingModule,
        FormsModule,
        ReactiveFormsModule,
        MtxGridModule,
        MatCheckboxModule,
        MatTabsModule,
        MatIconModule,
        MatButtonModule,
        MatTableModule,
        MatInputModule,
        MatProgressBarModule,
    ]
})
export class ProjectModule { }
