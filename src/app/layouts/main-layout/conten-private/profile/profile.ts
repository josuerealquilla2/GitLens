import { Component, OnInit, signal, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { PerfilService } from '../../../../core/services/usuario/perfil.service';
import { FriendsService } from '../../../../core/services/friends/friends.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  perfil        = signal<any>(null);
  cargando      = signal(true);
  editando      = signal(false);
  guardando     = signal(false);
  exito         = signal(false);
  errorMsg      = signal<string | null>(null);
  avatarPreview = signal<string | null>(null);

  selectedFile: File | null = null;

  form!: FormGroup;
  friendCount   = signal(0);
  pendingCount  = signal(0);

  user = (() => {
    try { return JSON.parse(localStorage.getItem('user') ?? '{}'); }
    catch { return {}; }
  })();

  constructor(private perfilService: PerfilService, private fb: FormBuilder, private friends: FriendsService) {}

  ngOnInit() {
    this.form = this.fb.group({
      bio:      [''],
      location: [''],
      website:  [''],
    });

    this.friends.getFriendCount().subscribe({
      next: (data) => {
        this.friendCount.set(data.friend_count);
        this.pendingCount.set(data.pending_requests);
      },
    });

    this.perfilService.getMiPerfil().subscribe({
      next: (data) => {
        this.perfil.set(data);
        if (data.image) this.avatarPreview.set(data.image);
        this.form.patchValue({
          bio:      data.bio ?? '',
          location: data.location ?? '',
          website:  data.website ?? '',
        });
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false),
    });
  }

  onAvatarClick() {
    if (!this.editando()) this.editando.set(true);
    this.fileInput.nativeElement.click();
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => this.avatarPreview.set(e.target?.result as string);
    reader.readAsDataURL(file);
    // Reset input so same file can be re-selected if needed
    input.value = '';
  }

  guardar() {
    this.guardando.set(true);
    this.exito.set(false);
    this.errorMsg.set(null);

    const onSuccess = (data: any) => {
      this.perfil.set(data);
      if (data.image) this.avatarPreview.set(data.image);
      this.selectedFile = null;
      this.guardando.set(false);
      this.editando.set(false);
      this.exito.set(true);
      setTimeout(() => this.exito.set(false), 3000);
    };
    const onError = (err: any) => {
      this.guardando.set(false);
      const data = err?.error;
      if (data?.website) this.errorMsg.set('Sitio web: ' + data.website[0]);
      else if (data?.bio)  this.errorMsg.set('Bio: ' + data.bio[0]);
      else this.errorMsg.set('Error al guardar. Revisa los campos e inténtalo de nuevo.');
    };

    if (this.selectedFile) {
      const fd = new FormData();
      fd.append('image', this.selectedFile);
      const v = this.form.value;
      fd.append('bio',      v.bio      ?? '');
      fd.append('location', v.location ?? '');
      fd.append('website',  v.website  ?? '');
      this.perfilService.actualizarPerfil(fd).subscribe({ next: onSuccess, error: onError });
    } else {
      this.perfilService.actualizarPerfil(this.form.value).subscribe({ next: onSuccess, error: onError });
    }
  }

  cancelar() {
    this.editando.set(false);
    this.selectedFile = null;
    // Restore preview to saved image
    const img = this.perfil()?.image;
    this.avatarPreview.set(img ?? null);
    this.form.patchValue({
      bio:      this.perfil()?.bio ?? '',
      location: this.perfil()?.location ?? '',
      website:  this.perfil()?.website ?? '',
    });
  }

  iniciales(): string {
    const n = this.user?.nombre ?? '';
    const a = this.user?.apellidos ?? '';
    return `${n[0] ?? ''}${a[0] ?? ''}`.toUpperCase() || '?';
  }

  fechaDesde(): string {
    const f = this.perfil()?.created_at;
    if (!f) return '';
    return new Date(f).toLocaleDateString('es-ES', { year: 'numeric', month: 'long' });
  }
}
