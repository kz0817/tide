document.addEventListener('DOMContentLoaded', () => {
    showFileList('/');
});

interface DirEntry {
  name: string;
  isDir: boolean;
  size: number;
  modifiedTime: string;
}

interface FileList {
  location: string;
  entries: DirEntry[];
}

const showFileList = async (dir: string): Promise<void> => {
  const url = `/api/filelist?location=${dir}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to call {url}`)
  }
  console.log(response);
  const fileList: FileList = await response.json();
  console.log(fileList);

  document.getElementById('location')!.textContent = fileList.location;

  const entriesElem: HTMLUListElement = document.getElementById('entries') as HTMLUListElement;

  fileList.entries
  .map((entry: DirEntry) => {
    const liElem = document.createElement('li');
    liElem.textContent = entry.name;
    return liElem;
  })
  .forEach((liElem: HTMLLIElement) => entriesElem.appendChild(liElem));
}
