import {Component, OnInit, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ReposSinRegistroService} from '../../../core/services/reposSinRegistro/repos-sin-registro.service';

type repo={
  "name": string
  "description":string
  "avatar": string
  "creador": string
  "lenguaje": string
  "numerodeEstrellas":number
  "urlRepos": string
}


@Component({
  selector: 'app-repos-sin-registro',
  imports: [

  ],
  templateUrl: './repos-sin-registro.html',
  styleUrl: './repos-sin-registro.scss',
})
export class ReposSinRegistro implements OnInit{
  constructor(
    private repos:ReposSinRegistroService
  ) {}

  ListaRepos=signal<repo[]>([])


  ngOnInit(): void {
        this.repos.getReposSinRegistro().subscribe({
          next:data =>{
            this.ListaRepos.set(data)
          }
        })
    }





}
