import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SocialService } from '../../core/services/social/social.service';
import { ProfanityPipe } from '../profanity.pipe';

@Component({
  selector: 'app-comments-section',
  standalone: true,
  imports: [CommonModule, FormsModule, ProfanityPipe],
  templateUrl: './comments-section.html',
  styleUrl: './comments-section.scss',
})
export class CommentsSectionComponent implements OnInit {
  @Input() repoId!: string;
  @Input() isAuthenticated = false;

  comments = signal<any[]>([]);
  newBody = '';
  replyingTo = signal<number | null>(null);
  replyBody = '';
  loading = signal(false);

  readonly currentUserEmail: string = (() => {
    try { return JSON.parse(localStorage.getItem('user') ?? '{}').email ?? ''; }
    catch { return ''; }
  })();

  constructor(private social: SocialService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.social.getComments(this.repoId).subscribe({
      next: (data) => { this.comments.set(data); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  submit() {
    if (!this.newBody.trim()) return;
    this.social.postComment(this.repoId, this.newBody.trim()).subscribe({
      next: (c) => {
        this.comments.update(list => [...list, c]);
        this.newBody = '';
      }
    });
  }

  submitReply(parentId: number) {
    if (!this.replyBody.trim()) return;
    this.social.postComment(this.repoId, this.replyBody.trim(), parentId).subscribe({
      next: () => {
        this.replyingTo.set(null);
        this.replyBody = '';
        this.load();
      }
    });
  }

  startReply(id: number) {
    this.replyingTo.set(this.replyingTo() === id ? null : id);
    this.replyBody = '';
  }

  deleteComment(id: number) {
    this.social.deleteComment(id).subscribe({
      next: () => this.comments.update(list => list.filter(c => c.id !== id))
    });
  }

  timeAgo(dateStr: string): string {
    const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
    if (diff < 60) return 'ahora mismo';
    if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
    if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`;
    return `hace ${Math.floor(diff / 86400)} días`;
  }
}
