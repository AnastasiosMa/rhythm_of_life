path = 'data/spotify_previews';
addpath(genpath('~/Documents/MATLAB/Matlab toolboxes/MIRtoolbox1.8.2'))
preview_folders = dir('data/spotify_previews/');
if preview_folders(3).name=='.DS_Store'
   preview_folders = preview_folders(4:end);
end
if exist('data/features/mirtempo_completed_folders.csv')==2
    completed_folders = table2array(readtable('data/features/mirtempo_completed_folders.csv',...
        'ReadVariableNames',false,'Delimiter',' '));
    features = readtable('data/features/mirtempo.csv');
    preview_folders = setdiff({preview_folders.name},completed_folders)';
else
    completed_folders = {};
    features = table('Size',[0,2],'VariableTypes',{'cell','double'},'VariableNames',{'Track','mirtempo'});
    preview_folders = {preview_folders.name};
end
for i = 1:length(preview_folders)
    if ~isempty(dir(['data/spotify_previews/' preview_folders{i} '/*.mp3']))
        cd(['data/spotify_previews/' preview_folders{i}])
        disp(preview_folders{i})
        a = mirtempo('Folder');
        tempo = mirgetdata(a);
        filenames=get(a,'Name');
        t = table(filenames',tempo','VariableNames',{'Track','mirtempo'});
        features = [features; t];
        cd ../../../
        writetable(features,'data/features/mirtempo.csv');
    end
    completed_folders = [completed_folders; preview_folders{i}];
    writetable(table(completed_folders),'data/features/mirtempo_completed_folders.csv','WriteVariableNames',false)
end