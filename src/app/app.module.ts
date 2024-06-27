import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { UploadComponent } from './upload/upload.component';  // Import UploadComponent here
import { UploadService } from './upload.service';  // Import UploadService here

@NgModule({
  declarations: [
    UploadComponent  // Only include components, directives, and pipes here
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [UploadService],
  bootstrap: [UploadComponent]  // Bootstrap the UploadComponent or another appropriate component
})
export class AppModule { }
