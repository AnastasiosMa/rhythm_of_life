path = 'data/spotify_previews';
addpath(genpath('~/Documents/MATLAB/Matlab toolboxes/MIRtoolbox1.8.2'))
preview_folders = dir('data/spotify_previews/');
if preview_folders(3).name=='.DS_Store'
   preview_folders = preview_folders(4:end); 
end
if exist('data/features/mirtempo_completed_folders.csv')==2
   completed_folders = readtable('data/features/mirtempo_completed_folders.csv');
   features = writetable(t,'data/features/mirtempo.csv');
   preview_folders = setdiff(preview_folders,completed_folders);
else
   completed_folders = {};
   features = table('Size',[0,2],'VariableTypes',{'cell','double'},'VariableNames',{'Track','mirtempo'});
end
for i = 1:length(preview_folders)
    cd(['data/spotify_previews/' preview_folders(i).name])
    a = mirtempo('Folder');
    tempo = mirgetdata(a);
    filenames=get(a,'Name');
    t = table(filenames',tempo','VariableNames',{'Track','mirtempo'});
    features = [features; t];
    cd ../../../
    writetable(t,'data/features/mirtempo.csv');
    completed_folders = [completed_folders preview_folders(i).name]; 
    writetable(t,'data/features/mirtempo_completed_folders.csv')
end