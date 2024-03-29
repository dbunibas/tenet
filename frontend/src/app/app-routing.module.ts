import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { AuthGuard } from './guard/auth.guard';
import { LoginComponent } from './routes/login/login.component';
import { NewProjectComponent } from './routes/new-project/new-project.component';
import { ProjectsResolver } from './service/resolver/projects.resolver';
import { ProjectResolver } from "./service/resolver/project.resolver";
import { ProjectComponent } from "./routes/project/project.component";
import { ExportsComponent } from './routes/exports/exports.component';
import { ExportsResolver } from './service/resolver/exports.resolver';

const routes: Routes = [
  { path: '', redirectTo: '/new', pathMatch: 'full' },
  { path: 'new', component: NewProjectComponent, canActivate: [AuthGuard], resolve: [ProjectsResolver] },
  // { path: 'project', component: ProjectComponent, canActivate: [AuthGuard], resolve: [ProjectResolver] },
  {
    path: 'project',
    loadChildren: () => import('./routes/project/project.module').then(m => m.ProjectModule),
    canActivate: [AuthGuard], resolve: [ProjectResolver]
  },
  { path: 'login', component: LoginComponent },
  { path: 'exports', component: ExportsComponent, canActivate: [AuthGuard], resolve: [ExportsResolver]},
  { path: '**', component: PageNotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
