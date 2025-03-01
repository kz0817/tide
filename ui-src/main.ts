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

const createDirItemElement = (entry: DirEntry, currDir: string): HTMLElement => {
  const elem: HTMLAnchorElement = document.createElement('a');
  elem.textContent = entry.name;
  elem.href = '#';
  elem.addEventListener('click', (event: MouseEvent) => {
      const parentDir: string = (currDir == '/') ? '' : currDir;
      showFileList(`${parentDir}/${entry.name}`);
  });
  return elem;
}

const createFileItemElement = (entry: DirEntry, currDir: string): HTMLElement => {
  const elem: HTMLAnchorElement = document.createElement('a');
  elem.textContent = entry.name;
  elem.href = `/api/file?location=${currDir}/${entry.name}`;
  elem.download=entry.name;
  return elem;
}

const createEntryElement = (entry: DirEntry, currDir: string): HTMLElement => {
  return entry.isDir
         ? createDirItemElement(entry, currDir)
         : createFileItemElement(entry, currDir);
}

const removeAllChildren = (elem: HTMLElement): void => {
  while (elem.firstChild) {
    elem.removeChild(elem.firstChild);
  }
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
  removeAllChildren(entriesElem);

  fileList.entries
  .map((entry: DirEntry) => {
    const liElem = document.createElement('li');
    liElem.appendChild(createEntryElement(entry, dir));
    return liElem;
  })
  .forEach((liElem: HTMLLIElement) => entriesElem.appendChild(liElem));
}
